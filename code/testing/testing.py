from code.nbody.bodies import Body
from code.nbody.engine import Simulation, SimulationConfig
from code.nbody.integrators.leapfrog import LeapfrogIntegrator
from code.nbody.solvers.barneshut import BarnesHutSolver
import matplotlib.pyplot as plt
import math

sun = Body(
    1.0,
    0.0, 0.0, 0.0,
    0.0, -0.001 * 2 * math.pi, 0.0
)

planet = Body(
    0.001,
    1.0, 0.0, 0.0,
    0.0, 2 * math.pi, 0.1
)

cfg = SimulationConfig(dt=2e-4, timesteps=5000, softening=0.0)

sim = Simulation([sun, planet], cfg, integrator=LeapfrogIntegrator(), solver = BarnesHutSolver(theta=0.5))
sim.run()

plt.figure()
plt.plot(sim.energy_drift)
plt.title("Relative Energy Drift")

plt.figure()
plt.plot(sim.angular_momentum_drift)
plt.title("Angular Momentum Drift")

plt.figure()
plt.plot(sim.linear_momentum_drift)
plt.title("|P(t)|")

plt.figure()
plt.plot(sim.com_drift)
plt.title("Center-of-Mass Drift")

plt.show()