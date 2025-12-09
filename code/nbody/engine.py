## holds configurations of the simulation & simulation itself and runs it


import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from typing import List

from nbody.bodies import Body, SystemState
from nbody.physics import compute_accelerations
from nbody.integrators.euler import EulerIntegrator

from nbody.solvers.direct import DirectSolver


class SimulationConfig: 

    def __init__(self, bodies, cfg, integrator=None, solver=None):
        self.state = SystemState(bodies)
        self.cfg = cfg
        self.integrator = integrator or EulerIntegrator()
        self.solver = solver or DirectSolver()


class Simulation:

    def __init__(self, bodies: List[Body], cfg: SimulationConfig, integrator=None):
        self.state = SystemState(bodies)
        self.cfg = cfg
        self.integrator = integrator or EulerIntegrator()

    def run(self):
       
        pss = [None] * (self.cfg.timesteps + 1)
        pss[0] = self.state.bodies

        for t in range(self.cfg.timesteps):
            # delegate time-stepping to the integrator
            self.state = self.integrator.step(
                self.state,
                self.cfg,
                self.solver.accelerations
            )
            pss[t + 1] = self.state.bodies

        return pss

    def closestDistance(self):
        import math

        ret = None
        pss = self.run()

        for step in pss:
            for a in step:
                for b in step:
                    if a is not b:
                        d = a.squareDist(b)
                        if ret is None or d < ret:
                            ret = d

        return None if ret is None else math.sqrt(ret)

    def show(self, x0, y0, x1, y1):
       
        pss = self.run()

        fig, ax = plt.subplots()
        ax.set_xlim(x0, x1)
        ax.set_ylim(y0, y1)

        scatters = [
            ax.scatter([], [], label=f"Body {i}")
            for i in range(len(self.state.bodies))
        ]

        time_text = ax.text(
            0.02, 0.98, '',
            transform=ax.transAxes,
            verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5)
        )

        def update(frame):
            for i, sc in enumerate(scatters):
                sc.set_offsets([pss[frame][i].x, pss[frame][i].y])
            time_text.set_text(f"Timestep: {frame}")
            return scatters + [time_text]

        FuncAnimation(
            fig, update,
            frames=len(pss),
            interval=1,
            blit=True,
            repeat=False
        )

        ax.set_xlabel("X coordinate (AU)")
        ax.set_ylabel("Y coordinate (AU)")
        ax.set_title("Celestial Body Trajectories")
        ax.legend()
        plt.show()