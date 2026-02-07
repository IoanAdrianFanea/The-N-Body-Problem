import math
from typing import List
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

from code.nbody.bodies import Body, SystemState
from code.nbody.integrators.euler import EulerIntegrator
from code.nbody.solvers.direct import DirectSolver
from code.nbody.solvers.barneshut import BarnesHutSolver
from code.nbody.physics import (
    compute_kinetic_energy,
    compute_potential_energy,
    compute_angular_momentum,
    compute_linear_momentum,
    compute_center_of_mass,
)


class SimulationConfig:
    def __init__(self, dt, timesteps, softening=0.001):
        self.dt = dt
        self.timesteps = timesteps
        self.softening = softening

        self.record_history: bool = False
        self.diagnostics_every: int = 1
        self.enable_diagnostics: bool = False
        self.record_frames: bool = False
        self.frame_every : int = 1


class Simulation:
    def __init__(self, bodies: List[Body], cfg: SimulationConfig, integrator=None, solver=None):
        self.state = SystemState(bodies)
        self.cfg = cfg
        self.integrator = integrator or EulerIntegrator()
        self.solver = solver or DirectSolver() or BarnesHutSolver()

        self.state_history = []

        self.kinetic_history = []
        self.potential_history = []
        self.energy_history = []
        self.energy_drift = []

        self.angular_momentum_history = []
        self.angular_momentum_drift = []

        self.linear_momentum_history = []
        self.linear_momentum_drift = []

        self.com_history = []
        self.com_drift = []
        
        self.frames = []


    def run(self):
        self._clear_histories()
        accel_fn = self._initialize_simulation()

        pss = None
        if self.cfg.record_history:
            pss = []
            pss.append([(b.x, b.y, b.z) for b in self.state.bodies])

        for step in range(self.cfg.timesteps):
            self._step(accel_fn, step)
            if pss is not None:
                pss.append([(b.x, b.y, b.z) for b in self.state.bodies])

        return pss
    

    def _initialize_simulation(self):
        def accel_fn(bodies):
            return self.solver.accelerations(bodies, self.cfg)

        self.state = self.integrator.initialize(self.state, self.cfg, accel_fn) #prepares for leapfrog (correct for integrating but not for measuring)
        diag = self.integrator.synchronize(self.state, self.cfg, accel_fn) #this is actually never integrated, only for measuring

        if self.cfg.record_history:
            self.state_history.append(diag.copy()) #stores diagnostics

        if self.cfg.record_frames:
            self.frames.append([(b.x, b.y, b.z) for b in diag.bodies])

        if self.cfg.enable_diagnostics:
            K0 = compute_kinetic_energy(diag.bodies)
            U0 = compute_potential_energy(diag.bodies, self.cfg)
            E0 = K0 + U0
            L0 = compute_angular_momentum(diag.bodies)
            P0 = compute_linear_momentum(diag.bodies)
            x_cm0, y_cm0, z_cm0 = compute_center_of_mass(diag.bodies)
            L0_mag = math.sqrt(L0[0]**2 + L0[1]**2 + L0[2]**2)

            self.E0 = E0
            self.L0 = L0
            self.P0 = P0
            self.com0 = (x_cm0, y_cm0, z_cm0)
            self.L0_mag = L0_mag

            self._update_diagnostics(diag, is_initial=True)
        return accel_fn
    

    def _step(self, accel_fn, step):
        self.state = self.integrator.step(self.state, self.cfg, accel_fn)
        diag = self.integrator.synchronize(self.state, self.cfg, accel_fn)

        if self.cfg.record_history:
            self.state_history.append(diag.copy())

        if self.cfg.record_frames and (step + 1) % self.cfg.frame_every == 0:
            self.frames.append([(b.x, b.y, b.z) for b in diag.bodies])

        if self.cfg.enable_diagnostics and (step + 1) % self.cfg.diagnostics_every == 0:
            self._update_diagnostics(diag)


    def _update_diagnostics(self, diag, is_initial=False): #measures the system, stores the raw values and computes drifts 
        K = compute_kinetic_energy(diag.bodies)
        U = compute_potential_energy(diag.bodies, self.cfg)
        E = K + U
        L = compute_angular_momentum(diag.bodies)
        P = compute_linear_momentum(diag.bodies)
        x_cm, y_cm, z_cm = compute_center_of_mass(diag.bodies)

        L_mag = math.sqrt(L[0]**2 + L[1]**2 + L[2]**2)
        self.angular_momentum_history.append(L_mag)

        self.kinetic_history.append(K)
        self.potential_history.append(U)
        self.energy_history.append(E)

        if is_initial:
            self.E0 = E
            self.E_scale = max(abs(E), abs(K) + abs(U), 1e-12)
            self.energy_drift.append(0.0)

            print(f"[diagnostics] E0={self.E0:.6e}, K0={K:.6e}, U0={U:.6e}, E_scale={self.E_scale:.6e}")
        else:
            den = self.E_scale
            drift = abs(E - self.E0) / den if den > 0 else 0.0
            self.energy_drift.append(drift)

            if len(self.energy_drift) <= 5:
                print(f"[diagnostics] step={len(self.energy_drift)-1} E={E:.6e} drift={drift:.6e}")

        if is_initial:
            self.angular_momentum_drift.append(0.0)
        else:
            if self.L0_mag > 1e-14:
                self.angular_momentum_drift.append(
                    (L_mag - self.L0_mag) / self.L0_mag
                )
            else:
                self.angular_momentum_drift.append(L_mag)

        self.linear_momentum_history.append(P)
        self.linear_momentum_drift.append(0.0 if is_initial else math.sqrt(P[0] ** 2 + P[1] ** 2 + P[2] ** 2))

        self.com_history.append((x_cm, y_cm, z_cm))
        if is_initial:
            self.com_drift.append(0.0)
        else:
            dx = x_cm - self.com0[0]
            dy = y_cm - self.com0[1]
            dz = z_cm - self.com0[2]
            self.com_drift.append(math.sqrt(dx * dx + dy * dy + dz * dz))


    def _clear_histories(self):
        self.state_history.clear()

        self.kinetic_history.clear()
        self.potential_history.clear()
        self.energy_history.clear()
        self.energy_drift.clear()

        self.angular_momentum_history.clear()
        self.angular_momentum_drift.clear()

        self.linear_momentum_history.clear()
        self.linear_momentum_drift.clear()

        self.com_history.clear()
        self.com_drift.clear()

        self.frames.clear()


    def show(self, x0, y0, x1, y1):
        pss = self.run()

        fig, ax = plt.subplots()
        ax.set_xlim(x0, x1)
        ax.set_ylim(y0, y1)

        scatters = [ax.scatter([], []) for _ in range(len(self.state.bodies))]

        def update(frame):
            for i, sc in enumerate(scatters):
                sc.set_offsets(pss[frame][i])
            return scatters

        FuncAnimation(fig, update, frames=len(pss), interval=1, blit=True, repeat=False)
        plt.show()