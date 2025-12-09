## Implements the Euler integration method for updating the state of the system

##it asks the solver for accelerations and uses them to update positions and velocities, then returns the system 


from nbody.bodies import Body, SystemState
from nbody.integrators import Integrator


class EulerIntegrator(Integrator):

    def step(self, state, cfg, accel_fn):
        
        bodies = state.bodies
        dt = cfg.dt

        # compute accelerations for all bodies
        ax, ay = accel_fn(bodies)

        new_bodies = []
        for i, b in enumerate(bodies):
            nb = Body(b.m, b.x, b.y)

            # update positions (same formula as old Simulation.run)
            nb.x = b.x + dt * b.vx + 0.5 * dt * dt * ax[i]
            nb.y = b.y + dt * b.vy + 0.5 * dt * dt * ay[i]

            # update velocities
            nb.vx = (nb.x - b.x) / dt
            nb.vy = (nb.y - b.y) / dt

            new_bodies.append(nb)

        return SystemState(new_bodies)