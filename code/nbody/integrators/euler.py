## Implements the Euler integration method for updating the state of the system

##it asks the solver for accelerations and uses them to update positions and velocities, then returns the system 


from code.nbody.bodies import Body, SystemState
from code.nbody.integrators import Integrator


class EulerIntegrator(Integrator):

    def step(self, state, cfg, accel_fn):
        
        bodies = state.bodies
        dt = cfg.dt

        # compute accelerations for all bodies
        ax, ay, az = accel_fn(bodies)

        new_bodies = []
        for i, b in enumerate(bodies):
            nb = Body(b.m, b.x, b.y, b.z)


            nb.vx = b.vx + dt * ax[i]
            nb.vy = b.vy + dt * ay[i]
            nb.vz = b.vz + dt * az[i]

            nb.x = b.x + dt * b.vx
            nb.y = b.y + dt * b.vy
            nb.z = b.z + dt * b.vz
            
            new_bodies.append(nb)

        return SystemState(new_bodies)
    

    def initialize(self, state, cfg, accel_fn):
        # no special initialization needed for Euler
        return state
    
    def synchronize(self, state, cfg, accel_fn):
        # no special synchronization needed for Euler
        return state