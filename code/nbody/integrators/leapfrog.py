from nbody.bodies import Body, SystemState
from nbody.integrators import Integrator


class LeapfrogIntegrator(Integrator): 

    def step(self, state, cfg, accel_fn):
        
        bodies = state.bodies
        dt = cfg.dt

        # 1) compute a_old
        ax_old, ay_old = accel_fn(bodies)

        # We'll store updated bodies 
        temp_bodies = []

        #half-step velocity update + FULL position update
        for i, b in enumerate(bodies):
            # half-step velocity
            vhx = b.vx + 0.5 * dt * ax_old[i]
            vhy = b.vy + 0.5 * dt * ay_old[i]

            # position update
            new_x = b.x + dt * vhx
            new_y = b.y + dt * vhy

            temp_bodies.append(Body(b.m, new_x, new_y, vhx, vhy)) #appends the body with UPDATED position but OLD half-step velocity

        # compute a_new from UPDATED positions
        ax_new, ay_new = accel_fn(temp_bodies)

        # second half-step velocity update
        new_bodies = []
        for i, b in enumerate(temp_bodies):
            vx_new = b.vx + 0.5 * dt * ax_new[i] #adjusting final velocity
            vy_new = b.vy + 0.5 * dt * ay_new[i]

            new_bodies.append(Body(b.m, b.x, b.y, vx_new, vy_new))

        return SystemState(new_bodies)





'''
 F = ma, acceleration needed


So at any time we know: mass, position and velocity of each body. Our goal is to update position and velocity over time.

dt is simply used for time step size.


Current formulas used:
F = G * m₁ * m₂ / r² (Newton's law of universal gravitation) (r = distance between bodies)

F = m * a → a = F / m (Newton's second law of motion)




Leapfrog will use half of the acceleration to update velocity first, then use that updated velocity to update position, then 
    compute the acceleration again to update velocity to the full step.



'''