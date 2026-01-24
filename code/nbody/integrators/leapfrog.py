from code.nbody.bodies import Body, SystemState
from code.nbody.integrators import Integrator


class LeapfrogIntegrator(Integrator):
    """
    Kick-Drift leapfrog storing velocities at half-step.
    Internal state:
      x = x^n
      v = v^{n+1/2}
    """

    def initialize(self, state, cfg, accel_fn):
        bodies = state.bodies
        dt = cfg.dt

        ax, ay, az = accel_fn(bodies)

        new_bodies = []
        for i, b in enumerate(bodies):
            # v^{1/2} = v^0 + 0.5*dt*a(x^0)
            vx_half = b.vx + 0.5 * dt * ax[i]
            vy_half = b.vy + 0.5 * dt * ay[i]
            vz_half = b.vz + 0.5 * dt * az[i]
            new_bodies.append(Body(b.m, b.x, b.y, b.z, vx_half, vy_half, vz_half))

        return SystemState(new_bodies, accel=(ax, ay, az))

    def step(self, state, cfg, accel_fn):
        bodies = state.bodies
        dt = cfg.dt

        # Drift: x^{n+1} = x^n + dt * v^{n+1/2}
        drifted = []
        for b in bodies:
            drifted.append(Body(
                b.m,
                b.x + dt * b.vx,
                b.y + dt * b.vy,
                b.z + dt * b.vz,
                b.vx,
                b.vy,
                b.vz
            ))

        # Kick: v^{n+3/2} = v^{n+1/2} + dt * a(x^{n+1})
        ax_new, ay_new, az_new = accel_fn(drifted)

        new_bodies = []
        for i, b in enumerate(drifted):
            vx_new = b.vx + dt * ax_new[i]
            vy_new = b.vy + dt * ay_new[i]
            vz_new = b.vz + dt * az_new[i]
            new_bodies.append(Body(b.m, b.x, b.y, b.z, vx_new, vy_new, vz_new))

        return SystemState(new_bodies, accel=(ax_new, ay_new, az_new))

    def synchronize(self, state, cfg, accel_fn):
        """
        Convert (x^n, v^{n+1/2}) -> (x^n, v^n) for diagnostics:
          v^n = v^{n+1/2} - 0.5*dt*a(x^n)
        """
        bodies = state.bodies
        dt = cfg.dt

        if state.accel is not None:
            ax, ay, az = state.accel
        else:
            ax, ay, az = accel_fn(bodies)

        synced = []
        for i, b in enumerate(bodies):
            vx_full = b.vx - 0.5 * dt * ax[i]
            vy_full = b.vy - 0.5 * dt * ay[i]
            vz_full = b.vz - 0.5 * dt * az[i]
            synced.append(Body(b.m, b.x, b.y, b.z, vx_full, vy_full, vz_full))

        return SystemState(synced)