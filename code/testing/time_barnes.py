import time
import random

#generated using AI assistance

from code.nbody.bodies import Body
from code.nbody.engine import Simulation, SimulationConfig
from code.nbody.integrators.leapfrog import LeapfrogIntegrator
from code.nbody.solvers.barneshut import BarnesHutSolver
from code.nbody.solvers.direct import DirectSolver


def make_random_bodies(N, seed=42):
    random.seed(seed)
    bodies = []
    for _ in range(N):
        bodies.append(
            Body(
                m=random.uniform(1e-3, 1e-2),
                x=random.uniform(-1, 1),
                y=random.uniform(-1, 1),
                z=random.uniform(-1, 1),
                vx=random.uniform(-0.5, 0.5),
                vy=random.uniform(-0.5, 0.5),
                vz=random.uniform(-0.5, 0.5),
            )
        )
    return bodies


N = 1000
steps = 300

cfg = SimulationConfig(dt=2e-3, timesteps=steps, softening=1e-3)
cfg.record_history = False
cfg.enable_diagnostics = False

sim = Simulation(
    bodies=make_random_bodies(N),
    cfg=cfg,
    integrator=LeapfrogIntegrator(),
    solver=BarnesHutSolver(theta=0.7),
)

sim2 = Simulation(
    bodies=make_random_bodies(N),
    cfg=cfg,
    integrator=LeapfrogIntegrator(),
    solver=DirectSolver(),
)

t0 = time.perf_counter()
sim.run()
t1 = time.perf_counter()

t2 = time.perf_counter()
sim2.run()
t3 = time.perf_counter()

print(f"Barnes–Hut runtime: {t1 - t0:.3f} s")
print(f"Direct runtime: {t3 - t2:.3f} s")