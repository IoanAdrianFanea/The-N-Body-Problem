<p align="center">
  <img src="assets/image.png" width="500">
</p>

<h1 align="center">The N-Body Problem</h1>

<p align="center">
  High-performance gravitational N-body simulation with Direct and Barnes–Hut solvers.<br>
  3D support • Symplectic integration • Profiling & optimization • Visualization pipeline
</p>

---


# Modular N-Body Simulation Engine (Python)

A long-term portfolio project focused on building a modular,
physics-based N-body simulation engine with emphasis on:

- Clean software architecture
- Numerical integration of Hamiltonian systems
- Solver design and interchangeability
- Scientific validation using conservation laws
- Performance profiling and scaling analysis

---

## Architecture Overview

The codebase follows strict separation of concerns:

- **Bodies** store physical state only  
- **Physics** is implemented as pure, stateless functions  
- **Solvers** compute accelerations (Direct, Barnes–Hut)  
- **Integrators** advance the system in time (Euler, Leapfrog)  
- **Engine** orchestrates simulation and diagnostics  
- **Visualization layer** handles plotting and animation  

This design allows solvers and integrators to be swapped
without modifying diagnostics or physics code.

---

## Current Status

Completed phases include:

- Architecture restructuring
- Symplectic integrator implementation (Leapfrog / Velocity Verlet)
- Full 3D extension
- Barnes–Hut octree solver
- Accuracy validation against Direct solver
- Scaling analysis (O(N²) vs O(N log N))
- Profiling and targeted performance optimization
- CLI runner and visualization system
- 2D and 3D animation with export support

The project is under active development.
Future work will focus on further optimization experiments
and documentation consolidation.

---

## Example Simulations

Below are example outputs generated directly from the CLI interface.


### Two-Body Orbit (Leapfrog, Direct Solver)

![Two Body Orbit](assets/anim_xyz_two_body.gif)

---

### Rotating Disk (Barnes–Hut)

![Disk Simulation | Initial](assets/initial_xyz_disk.png)

![Disk Simulation | Final](assets/final_xyz_disk.png)

---

### Three-Body Figure-Eight (3D Animation)

![Three Body 3D](assets/anim_xyz_three_body.gif)

---

### Energy Drift Comparison (Leapfrog vs Euler)

![Energy Drift | Euler](assets/energy_drift_euler.png)

![Energy Drift | Leapfrog](assets/energy_drift_leapfrog.png)

---

## Running the Simulation 

Basic orbit (2D):

```bash
python -m code.nbody.cli run --scene two_body --animate
```

Basic orbit (3D):

```bash
python -m code.nbody.cli run --scene two_body --animate-3d
```

---

## Benchmarking Direct vs Barnes–Hut

The `benchmark_cluster` scene is designed to demonstrate the
performance difference between the Direct O(N²) solver and
the Barnes–Hut O(N log N) solver for large N.

To benchmark fairly:
- Do NOT enable animation
- Do NOT enable plotting
- Use identical scene and integrator settings


Windows (PowerShell)
--------------------

Measure Barnes–Hut:

```powershell
Measure-Command { python -m code.nbody.cli run --scene benchmark_cluster --solver barneshut --integrator leapfrog }
```

Measure Direct:

```powershell
Measure-Command { python -m code.nbody.cli run --scene benchmark_cluster --solver direct --integrator leapfrog }
```

macOS / Linux (bash / zsh)
--------------------------

Measure Barnes–Hut:

```bash
time python -m code.nbody.cli run --scene benchmark_cluster --solver barneshut --integrator leapfrog
```

Measure Direct:

```bash
time python -m code.nbody.cli run --scene benchmark_cluster --solver direct --integrator leapfrog
```


Expected Result
---------------

For sufficiently large N:

- Direct runtime grows approximately O(N²)
- Barnes–Hut runtime grows approximately O(N log N)

Barnes–Hut should become significantly faster as N increases.
