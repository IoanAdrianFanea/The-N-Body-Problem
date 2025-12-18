import random
import math
import matplotlib.pyplot as plt

from code.nbody.bodies import Body
from code.nbody.engine import Simulation, SimulationConfig
from code.nbody.integrators.leapfrog import LeapfrogIntegrator
from code.nbody.solvers.direct import DirectSolver
from code.nbody.solvers.barneshut import BarnesHutSolver


def make_random_bodies(N, seed=0, pos_scale=1.0, vel_scale=0.5, m_min=1e-3, m_max=1e-2):
    random.seed(seed)
    bodies = []
    for _ in range(N):
        m = random.uniform(m_min, m_max)
        x = random.uniform(-pos_scale, pos_scale)
        y = random.uniform(-pos_scale, pos_scale)
        z = random.uniform(-pos_scale, pos_scale)
        vx = random.uniform(-vel_scale, vel_scale)
        vy = random.uniform(-vel_scale, vel_scale)
        vz = random.uniform(-vel_scale, vel_scale)
        bodies.append(Body(m, x, y, z, vx, vy, vz))
    return bodies


def run_sim(bodies, solver, dt=2e-3, steps=2000, softening=1e-3):
    cfg = SimulationConfig(dt=dt, timesteps=steps, softening=softening)
    sim = Simulation(bodies, cfg, integrator=LeapfrogIntegrator(), solver=solver)
    sim.run()
    return sim


N = 15
seed = 42

bodies0 = make_random_bodies(N, seed=seed)

sim_direct = run_sim([Body(*b.asTuple()) for b in bodies0], DirectSolver())
sim_bh = run_sim([Body(*b.asTuple()) for b in bodies0], BarnesHutSolver(theta=1))

plt.figure()
plt.plot(sim_direct.energy_drift, label="Direct")
plt.plot(sim_bh.energy_drift, label="Barnes–Hut θ=1")
plt.title("Relative Energy Drift")
plt.legend()

plt.figure()
plt.plot(sim_direct.angular_momentum_drift, label="Direct")
plt.plot(sim_bh.angular_momentum_drift, label="Barnes–Hut θ=1")
plt.title("Angular Momentum Drift")
plt.legend()

plt.figure()
plt.plot(sim_direct.linear_momentum_drift, label="Direct")
plt.plot(sim_bh.linear_momentum_drift, label="Barnes–Hut θ=1")
plt.title("|P(t)|")
plt.legend()

plt.figure()
plt.plot(sim_direct.com_drift, label="Direct")
plt.plot(sim_bh.com_drift, label="Barnes–Hut θ=1")
plt.title("Center-of-Mass Drift")
plt.legend()

plt.show()