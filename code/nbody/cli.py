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
    if name == "two_body":
        return scenes.two_body()

    if name == "three_body":
        return scenes.three_body()

    if name == "random_cluster":
        return scenes.random_cluster(n=500, seed=42)

    if name == "disk":
        return scenes.disk(n=300)

    raise ValueError(f"Unknown scene '{name}'")


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
            "and integrator. All parameters are optional and have sensible defaults."
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

    sim_group = run_parser.add_argument_group("Simulation parameters")
    sim_group.add_argument(
        "--dt",
        type=check_dt,
        default=0.002,
        help="Time step size (defaults to 0.002)",
    )
    sim_group.add_argument(
        "--steps",
        type=check_steps,
        default=2000,
        help="Number of integration steps (defaults to 2000)",
    )
    sim_group.add_argument(
        "--softening",
        type=float,
        default=1e-3,
        help="Gravitational softening length (defaults to 0.001)",
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
        default=5,
        help="Record one animation frame every N steps (defaults to 5)",
    )
    output_group.add_argument(
        "--interval",
        type=int,
        default=20,
        help="Animation frame interval in ms (defaults to 20)",
    )

    subparsers.add_parser(
        "list-scenes",
        help="List available predefined scenes",
    )
    

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
        print("Available scenes:")
        for s in SCENES:
            print(f"  - {s}")
        return 0

    if args.command == "run":
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

        if args.plots:
            # Create output directory for this run
            run_dir = make_run_dir(
                outputs_dir="outputs",
                scene=args.scene,
                solver=args.solver,
                integrator=args.integrator,
                n=len(sim.state.bodies),
            )

            title_prefix = (
                f"{args.scene} | {args.solver} | {args.integrator} | "
                f"N={len(sim.state.bodies)}"
            )

            saved_files = save_stepc_outputs(
                sim,
                run_dir,
                title_prefix=title_prefix,
            )

            print(f"\nPlots saved to: {run_dir}")
            for path in saved_files:
                print(f"  - {path.name}")

        if args.animate:
            title_prefix = (
                f"{args.scene} | {args.solver} | {args.integrator} | "
                f"N={len(sim.state.bodies)}"
            )
            animate_xy(
                sim.frames,
                out_path=None,
                interval=args.interval,
                title=title_prefix,
                show=True,
            )


        print("\nSimulation complete")
        print(f"Scene:       {args.scene}")
        print(f"Solver:      {args.solver}")
        print(f"Integrator:  {args.integrator}")
        print(f"Bodies:      {len(bodies)}")
        print(f"Steps:       {args.steps}")
        print(f"dt:          {args.dt}")

        if args.energy and sim.energy_history:
            print(f"Final energy: {sim.energy_history[-1]:.6e}")

        return 0

    return 1


if __name__ == "__main__":
    raise SystemExit(main())