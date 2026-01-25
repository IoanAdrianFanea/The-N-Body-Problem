Documentation Overview

This folder contains logs, notes, and summaries documenting the development
of the N-body simulation project.

The documentation was written progressively throughout the project and
reflects both experimental results and architectural decisions made during
development. Earlier phases contain lighter documentation, while later phases
are documented in more detail as the project matured.

Structure Overview

- architecture_evolution.txt
  Describes how the project architecture evolved over time, including
  early misconceptions, design corrections, and the final modular structure.

- phases.txt
  High-level overview of all project phases, their goals, and completion status.

- EXPERIMENT_LOG.txt
  Chronological experiment and validation log.
  Contains detailed test setups, expected outcomes, observed results, and
  conclusions from physics and numerical validation experiments.

- barnes_hut_observations.txt
  Focused observations and conclusions related to the Barnes–Hut solver,
  including accuracy, stability, and approximation behavior.

Subfolders

- performance/
  Contains phase-specific performance and benchmarking results.
  These files focus on runtime scaling, profiling results, and solver
  comparisons for phases where performance analysis was a primary goal.

- track_changes/
  Records implementation changes and design decisions made during each phase.
  These files explain what was changed, why the change was made, and the
  resulting impact on correctness or performance.

Notes on Phase Documentation

Later phases (Phase 6 onward) include more structured documentation, including:
- explicit phase plans
- change tracking
- performance measurements
- reflections and conclusions

Earlier phases may not include all of these elements individually.
A retrospective summary for each phase is planned at the end of the project
to provide a consistent, complete overview of the full development process.

Reading Guide (Suggested)

1. phases.txt
2. architecture_evolution.txt
3. EXPERIMENT_LOG.txt
4. Phase-specific performance and change logs as needed