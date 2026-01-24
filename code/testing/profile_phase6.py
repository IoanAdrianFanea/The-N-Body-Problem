"""
Phase 6 profiling harness.

Uses Python's cProfile to identify performance hotspots in the N-body
simulation pipeline (Direct vs Barnes–Hut solvers under Leapfrog integration).

Initial profiling scaffold was developed with AI assistance and integrated
after review to guide optimization work.
"""



import cProfile
import pstats
import io
import random

from code.nbody.bodies import Body
from code.nbody.engine import Simulation, SimulationConfig
from code.nbody.integrators.leapfrog import LeapfrogIntegrator
from code.nbody.solvers.direct import DirectSolver
from code.nbody.solvers.barneshut import BarnesHutSolver


def make_random_bodies(N, seed=42, pos_scale=1.0, vel_scale=0.5, m_min=1e-3, m_max=1e-2):
    random.seed(seed)
    bodies = []
    for _ in range(N):
        bodies.append(
            Body(
                m=random.uniform(m_min, m_max),
                x=random.uniform(-pos_scale, pos_scale),
                y=random.uniform(-pos_scale, pos_scale),
                z=random.uniform(-pos_scale, pos_scale),
                vx=random.uniform(-vel_scale, vel_scale),
                vy=random.uniform(-vel_scale, vel_scale),
                vz=random.uniform(-vel_scale, vel_scale),
            )
        )
    return bodies


def run_case(N, steps, dt, softening, solver):
    cfg = SimulationConfig(dt=dt, timesteps=steps, softening=softening)
    cfg.record_history = False
    cfg.diagnostics_every = 1
    cfg.enable_diagnostics = False
    sim = Simulation(
        bodies=make_random_bodies(N, seed=42),
        cfg=cfg,
        integrator=LeapfrogIntegrator(),
        solver=solver,
    )
    sim.run()

    #print("Max energy drift:", max(abs(x) for x in sim.energy_drift) if sim.energy_drift else None)
    #print("Max COM drift:", max(sim.com_drift) if sim.com_drift else None)
    #print("Max |L| drift:", max(sim.angular_momentum_drift) if sim.angular_momentum_drift else None)
    #print("Max |P| drift:", max(sim.linear_momentum_drift) if sim.linear_momentum_drift else None)


def profile_case(label, N, steps, dt, softening, solver):
    pr = cProfile.Profile()
    pr.enable()
    run_case(N, steps, dt, softening, solver)
    pr.disable()

    s = io.StringIO()
    ps = pstats.Stats(pr, stream=s).strip_dirs().sort_stats("cumtime")
    ps.print_stats(30)  # top 30 by cumulative time
    print(f"\n==== {label} (top 30 by cumulative time) ====")
    print(s.getvalue())


if __name__ == "__main__":
    # Choose N so Direct is slow but finishes, and Barnes–Hut is representative
    dt = 2e-3
    steps = 300  # keep short for profiling; we want function breakdown, not long runs
    softening = 1e-3


    profile_case(
        "Barnes–Hut theta=0.7",
        N=1000,
        steps=300,
        dt=2e-3,
        softening=1e-3,
        solver=BarnesHutSolver(theta=0.7),
    )
    