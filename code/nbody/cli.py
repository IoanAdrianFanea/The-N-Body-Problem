from __future__ import annotations

import argparse
from typing import Optional, Sequence

from code.nbody.viz import make_run_dir, save_stepc_outputs, animate_xy
from code.nbody.engine import Simulation, SimulationConfig
from code.nbody.integrators.euler import EulerIntegrator
from code.nbody.integrators.leapfrog import LeapfrogIntegrator
from code.nbody.solvers.direct import DirectSolver
from code.nbody.solvers.barneshut import BarnesHutSolver
from code.nbody import scenes


SCENES = ("two_body", "three_body", "random_cluster", "disk")
SOLVERS = ("direct", "barneshut")
INTEGRATORS = ("euler", "leapfrog")


# Demo presets so the CLI stays minimal: `--scene X --animate` should look good.
# Users can still override via flags if they want.
SCENE_KWARGS = {
    "two_body": dict(),
    "three_body": dict(),
    "random_cluster": dict(
        n=500,
        seed=42,
        radius=3.0,
        mass_min=1e-3,
        mass_max=1e-2,
        v_scale=0.05,
    ),
    "disk": dict(
        n=300,
        seed=42,
        radius=5.0,
        mass=5e-2,
        v_scale=0.30,
        thickness=0.05,
    ),
}

RUN_PRESETS = {
    "two_body": dict(dt=0.002, steps=4000, softening=1e-3, frame_every=5, interval=30),
    "three_body": dict(dt=0.002, steps=6000, softening=1e-3, frame_every=5, interval=30),
    "random_cluster": dict(dt=0.001, steps=4000, softening=0.01, frame_every=25, interval=10),
    "disk": dict(dt=0.001, steps=5000, softening=0.002, frame_every=15, interval=10),
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

    subparsers = parser.add_subparsers(
        dest="command",
        required=True,
        help="Available commands",
    )

    run_parser = subparsers.add_parser(
        "run",
        help="Run a predefined simulation scene",
        description=(
            "Run a predefined N-body simulation using a chosen scene, solver, "
            "and integrator. Defaults are scene-tuned for clean demos."
        ),
    )

    scene_group = run_parser.add_argument_group("Scene selection")
    scene_group.add_argument(
        "--scene",
        choices=SCENES,
        default="two_body",
        help="Initial condition preset to simulate (defaults to two_body)",
    )

    method_group = run_parser.add_argument_group("Numerical methods")
    method_group.add_argument(
        "--solver",
        choices=SOLVERS,
        default="direct",
        help="Force solver to use: direct or barneshut (defaults to direct)",
    )
    method_group.add_argument(
        "--integrator",
        choices=INTEGRATORS,
        default="leapfrog",
        help="Time integrator to use: euler or leapfrog (defaults to leapfrog)",
    )
    method_group.add_argument(
        "--theta",
        type=float,
        default=0.7,
        help="Barnes–Hut opening angle (only used with barneshut solver)",
    )

    sim_group = run_parser.add_argument_group("Simulation parameters (optional overrides)")
    sim_group.add_argument(
        "--dt",
        type=check_dt,
        default=None,
        help="Time step size (defaults to scene preset)",
    )
    sim_group.add_argument(
        "--steps",
        type=check_steps,
        default=None,
        help="Number of steps (defaults to scene preset)",
    )
    sim_group.add_argument(
        "--softening",
        type=float,
        default=None,
        help="Softening length (defaults to scene preset)",
    )

    output_group = run_parser.add_argument_group("Diagnostics and output")
    output_group.add_argument(
        "--energy",
        action="store_true",
        help="Enable energy diagnostics",
    )
    output_group.add_argument(
        "--plots",
        action="store_true",
        help="Enable diagnostic plots",
    )
    output_group.add_argument(
        "--animate",
        action="store_true",
        help="Show 2D XY animation after running",
    )
    output_group.add_argument(
        "--frame-every",
        type=int,
        default=None,
        help="Record one animation frame every N steps (defaults to scene preset)",
    )
    output_group.add_argument(
        "--interval",
        type=int,
        default=None,
        help="Animation frame interval in ms (defaults to scene preset)",
    )

    subparsers.add_parser(
        "list-scenes",
        help="List available scenes and their demo presets",
    )


    output_group.add_argument("--save-gif", action="store_true", help="Save animation to outputs/... as GIF")
    output_group.add_argument("--save-mp4", action="store_true", help="Save animation to outputs/... as MP4 (ffmpeg required)")
    output_group.add_argument("--fps", type=int, default=30, help="FPS for saved animations (default: 30)")
    output_group.add_argument("--no-show", action="store_true", help="Do not open animation window (useful when saving)")

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
        # Apply scene-tuned demo presets only when user didn't override
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

        total_time = args.dt * args.steps

        if total_time > 50:
            print(
                f"Warning: total simulated time = {total_time:.2f}. "
                "This may be slow or unstable."
            )

        if args.steps > 100_000:
            print(
                f"Warning: steps = {args.steps}. "
                "This may take a long time to run."
            )

        bodies = load_scene(args.scene)

        cfg = SimulationConfig(
            dt=args.dt,
            timesteps=args.steps,
            softening=args.softening,
        )
        cfg.enable_diagnostics = args.energy or args.plots

        cfg.record_frames = args.animate
        cfg.frame_every = args.frame_every

        sim = Simulation(
            bodies=bodies,
            cfg=cfg,
            integrator=make_integrator(args.integrator),
            solver=make_solver(args.solver, args.theta),
        )

        sim.run()

        title_prefix = (
            f"{args.scene} | {args.solver} | {args.integrator} | "
            f"N={len(sim.state.bodies)}"
        )

        saving_anim = args.animate and (args.save_gif or args.save_mp4)

        run_dir = None
        if args.plots or saving_anim:
            run_dir = make_run_dir(
                outputs_dir="outputs",
                scene=args.scene,
                solver=args.solver,
                integrator=args.integrator,
                n=len(sim.state.bodies),
            )

        if args.plots:
            saved_files = save_stepc_outputs(
                sim,
                run_dir,
                title_prefix=title_prefix,
            )

            print(f"\nPlots saved to: {run_dir}")
            for path in saved_files:
                print(f"  - {path.name}")

        if args.animate:
            out_path = None
            if saving_anim:
                if args.save_gif:
                    out_path = run_dir / "anim_xy.gif"
                elif args.save_mp4:
                    out_path = run_dir / "anim_xy.mp4"

            saved = animate_xy(
                sim.frames,
                out_path=out_path,
                interval=args.interval,
                title=title_prefix,
                show=(not args.no_show),
                fps=args.fps,
            )

            if saved is not None:
                print(f"Animation saved to: {saved}")

        print("\nSimulation complete")
        print(f"Scene:       {args.scene}")
        print(f"Solver:      {args.solver}")
        print(f"Integrator:  {args.integrator}")
        print(f"Bodies:      {len(bodies)}")
        print(f"Steps:       {args.steps}")
        print(f"dt:          {args.dt}")
        print(f"softening:   {args.softening}")

        if args.energy and sim.energy_history:
            print(f"Final energy: {sim.energy_history[-1]:.6e}")

        return 0

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
