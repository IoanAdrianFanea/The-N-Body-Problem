from __future__ import annotations

import argparse
from typing import Optional, Sequence

from code.nbody.viz import make_run_dir, save_stepc_outputs, animate_xy, animate_xyz, save_snapshots_xyz
from code.nbody.engine import Simulation, SimulationConfig
from code.nbody.integrators.euler import EulerIntegrator
from code.nbody.integrators.leapfrog import LeapfrogIntegrator
from code.nbody.solvers.direct import DirectSolver
from code.nbody.solvers.barneshut import BarnesHutSolver
from code.nbody import scenes


SCENES = ("two_body", "three_body", "random_cluster", "disk", "benchmark_cluster")
SOLVERS = ("direct", "barneshut")
INTEGRATORS = ("euler", "leapfrog")

SCENE_KWARGS = {
    "two_body": dict(),
    "three_body": dict(),
    "random_cluster": dict(n=500, seed=42, radius=3.0, mass_min=1e-3, mass_max=1e-2, v_scale=0.05),
    "disk": dict(n=300, seed=42, radius=5.0, mass=5e-2, v_scale=0.30, thickness=0.05),
    "benchmark_cluster": dict(n=2500, seed=123, radius=5.0, mass_min=1e-3, mass_max=1e-2, v_scale=0.06, virialize=True),
}

RUN_PRESETS = {
    "two_body": dict(dt=0.002, steps=4000, softening=1e-3, frame_every=5, interval=30),
    "three_body": dict(dt=0.002, steps=6000, softening=1e-3, frame_every=5, interval=30),
    "random_cluster": dict(dt=0.001, steps=4000, softening=0.01, frame_every=25, interval=10),
    "disk": dict(dt=0.001, steps=5000, softening=0.002, frame_every=15, interval=10),
    "benchmark_cluster": dict(dt=0.001, steps=300, softening=0.01, frame_every=50, interval=10),
}


def check_dt(value: str) -> float:
    try:
        fvalue = float(value)
    except ValueError:
        raise argparse.ArgumentTypeError(f"{value} is not a valid float")
    if fvalue <= 0.0:
        raise argparse.ArgumentTypeError("dt must be a positive float")
    return fvalue


def check_steps(value: str) -> int:
    try:
        ivalue = int(value)
    except ValueError:
        raise argparse.ArgumentTypeError(f"{value} is not a valid integer")
    if ivalue <= 0:
        raise argparse.ArgumentTypeError("steps must be a positive integer")
    return ivalue


def load_scene(name: str):
    if name not in SCENES:
        raise ValueError(f"Unknown scene '{name}'")
    kwargs = SCENE_KWARGS.get(name, {})
    fn = getattr(scenes, name)
    return fn(**kwargs)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "N-body simulation command-line interface.\n\n"
            "Use the `run` command to execute a simulation. "
            "For full configuration options, run:\n\n"
            "  python -m code.nbody.cli run --help"
        )
    )

    subparsers = parser.add_subparsers(dest="command", required=True, help="Available commands")

    run_parser = subparsers.add_parser(
        "run",
        help="Run a predefined simulation scene",
        description=(
            "Run a predefined N-body simulation using a chosen scene, solver, "
            "and integrator. Defaults are scene-tuned for clean demos."
        ),
    )

    scene_group = run_parser.add_argument_group("Scene selection")
    scene_group.add_argument("--scene", choices=SCENES, default="two_body")

    method_group = run_parser.add_argument_group("Numerical methods")
    method_group.add_argument("--solver", choices=SOLVERS, default="direct")
    method_group.add_argument("--integrator", choices=INTEGRATORS, default="leapfrog")
    method_group.add_argument("--theta", type=float, default=0.7)

    sim_group = run_parser.add_argument_group("Simulation parameters (optional overrides)")
    sim_group.add_argument("--dt", type=check_dt, default=None)
    sim_group.add_argument("--steps", type=check_steps, default=None)
    sim_group.add_argument("--softening", type=float, default=None)

    output_group = run_parser.add_argument_group("Diagnostics and output")
    output_group.add_argument("--energy", action="store_true")
    output_group.add_argument("--plots", action="store_true")
    output_group.add_argument("--animate", action="store_true")
    output_group.add_argument("--frame-every", type=int, default=None)
    output_group.add_argument("--interval", type=int, default=None)
    output_group.add_argument("--save-gif", action="store_true")
    output_group.add_argument("--save-mp4", action="store_true")
    output_group.add_argument("--fps", type=int, default=30)
    output_group.add_argument("--no-show", action="store_true")
    output_group.add_argument("--animate-3d", action="store_true")
    output_group.add_argument("--max-3d-n", type=int, default=50)
    output_group.add_argument("--snapshots", action="store_true")

    subparsers.add_parser("list-scenes", help="List available scenes and their demo presets")
    return parser


def make_solver(name: str, theta: float):
    if name == "direct":
        return DirectSolver()
    return BarnesHutSolver(theta=theta)


def make_integrator(name: str):
    if name == "euler":
        return EulerIntegrator()
    return LeapfrogIntegrator()


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "list-scenes":
        print("Available scenes (demo presets):\n")
        for s in SCENES:
            sk = SCENE_KWARGS.get(s, {})
            rp = RUN_PRESETS.get(s, {})
            print(f"- {s}")
            print(f"  scene kwargs: {sk if sk else '{}'}")
            if rp:
                print(
                    "  run preset:   "
                    f"dt={rp.get('dt')}  steps={rp.get('steps')}  softening={rp.get('softening')}  "
                    f"frame_every={rp.get('frame_every')}  interval={rp.get('interval')}ms"
                )
            print()
        return 0

    if args.command == "run":
        preset = RUN_PRESETS.get(args.scene, {})

        if args.dt is None:
            args.dt = preset.get("dt", 0.002)
        if args.steps is None:
            args.steps = preset.get("steps", 2000)
        if args.softening is None:
            args.softening = preset.get("softening", 1e-3)
        if args.frame_every is None:
            args.frame_every = preset.get("frame_every", 5)
        if args.interval is None:
            args.interval = preset.get("interval", 30)

        bodies = load_scene(args.scene)

        cfg = SimulationConfig(dt=args.dt, timesteps=args.steps, softening=args.softening)
        cfg.enable_diagnostics = args.energy or args.plots

        needs_frames = args.animate or args.animate_3d or args.snapshots
        cfg.record_frames = needs_frames
        cfg.frame_every = args.frame_every

        sim = Simulation(
            bodies=bodies,
            cfg=cfg,
            integrator=make_integrator(args.integrator),
            solver=make_solver(args.solver, args.theta),
        )

        sim.run()

        N = len(sim.state.bodies)
        title_prefix = f"{args.scene} | {args.solver} | {args.integrator} | N={N}"

        want_3d = args.animate_3d
        small_enough = N <= args.max_3d_n
        fallback_to_snapshots = want_3d and not small_enough

        saving_anim = (args.animate or args.animate_3d) and (args.save_gif or args.save_mp4)
        needs_run_dir = args.plots or saving_anim or args.snapshots or fallback_to_snapshots

        run_dir = None
        if needs_run_dir:
            run_dir = make_run_dir("outputs", args.scene, args.solver, args.integrator, N)

        if args.plots:
            saved_files = save_stepc_outputs(sim, run_dir, title_prefix=title_prefix)
            print(f"\nPlots saved to: {run_dir}")
            for path in saved_files:
                print(f"  - {path.name}")

        if args.snapshots or fallback_to_snapshots:
            if fallback_to_snapshots:
                print(f"\n3D animation disabled (N={N} > {args.max_3d_n}). Saving 3D snapshots instead.")
            saved = save_snapshots_xyz(sim, run_dir, title_prefix=title_prefix)
            print(f"3D snapshots saved to: {run_dir}")
            for p in saved:
                print(f"  - {p.name}")

        if args.animate:
            out_path = None
            if saving_anim:
                out_path = run_dir / ("anim_xy.gif" if args.save_gif else "anim_xy.mp4")
            saved = animate_xy(sim.frames, out_path=out_path, interval=args.interval, title=title_prefix, show=(not args.no_show), fps=args.fps)
            if saved is not None:
                print(f"Animation saved to: {saved}")

        if want_3d and small_enough:
            out_path = None
            if saving_anim:
                out_path = run_dir / ("anim_xyz.gif" if args.save_gif else "anim_xyz.mp4")
            saved = animate_xyz(sim.frames, out_path=out_path, interval=args.interval, title=title_prefix, show=(not args.no_show), fps=args.fps)
            if saved is not None:
                print(f"3D animation saved to: {saved}")

        print("\nSimulation complete")
        print(f"Scene:       {args.scene}")
        print(f"Solver:      {args.solver}")
        print(f"Integrator:  {args.integrator}")
        print(f"Bodies:      {N}")
        print(f"Steps:       {args.steps}")
        print(f"dt:          {args.dt}")
        print(f"softening:   {args.softening}")

        if args.energy and sim.energy_history:
            print(f"Final energy: {sim.energy_history[-1]:.6e}")

        return 0

    return 1


if __name__ == "__main__":
    raise SystemExit(main())