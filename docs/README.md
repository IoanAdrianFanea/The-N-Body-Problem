
# Documentation Overview

This folder contains logs, notes, and summaries documenting
the development of the N-body simulation project.

Documentation was written progressively throughout development
and reflects architectural decisions, numerical validation,
and performance experiments.

---

## Structure Overview

### architecture_evolution.txt
Explains how the architecture evolved over time, including:

- Early misconceptions
- Integrator corrections
- Separation of concerns
- Final modular structure

---

### phases.txt
High-level overview of all project phases and their completion status.

---

### EXPERIMENT_LOG.txt
Chronological experiment and validation log including:

- Test setups
- Expected physical behavior
- Observed results
- Conclusions from numerical validation

---

### barnes_hut_observations.txt
Focused observations on the Barnes–Hut solver:

- Accuracy behavior vs θ
- Stability analysis
- Approximation trade-offs

---

## Subfolders

### performance/
Contains runtime measurements, profiling results,
and solver comparisons from performance-focused phases.

### track_changes/
Records implementation changes made during each phase,
including reasoning and resulting impact.

---

## Documentation Philosophy

- Logs reflect real development progression.
- Validation is grounded in physical invariants.
- Performance decisions are based on measured data.
- Later phases contain more structured documentation
  as project maturity increased.

---

## Suggested Reading Order

1. phases.txt  
2. architecture_evolution.txt  
3. EXPERIMENT_LOG.txt  
4. Phase-specific performance logs  
5. Change tracking files  

---

This documentation is intended to demonstrate not only
what was built, but how and why architectural decisions
were made throughout the project.