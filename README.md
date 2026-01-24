Modular N-Body Simulation Engine (Python)

This project is a long-term portfolio project focused on building a modular,
physics-based N-body simulation engine with an emphasis on:

- Clean software architecture
- Numerical integration of Hamiltonian systems
- Solver design and interchangeability
- Scientific validation using conservation laws
- Performance profiling and scaling analysis

The codebase is organized around clear separation of concerns:
- Bodies store physical state only
- Physics is implemented as pure, stateless functions
- Solvers compute accelerations (Direct, Barnes–Hut)
- Integrators advance the system in time (Euler, Leapfrog)
- The engine orchestrates simulation and diagnostics

Current Status
The project is under active development.
Phases up to Barnes–Hut implementation, validation, and targeted performance
optimization are complete.
Future phases will focus on visualization, interface improvements, and
additional optimization experiments.

This repository emphasizes clarity, correctness, and reasoning over
premature optimization.