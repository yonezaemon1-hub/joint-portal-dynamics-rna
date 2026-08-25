# Reproduction notes

## Environment used for the frozen reference run

- Windows 10 build 19045
- Python 3.10.11
- NumPy 2.2.6
- SciPy 1.15.3
- ViennaRNA 2.7.2

## Published parameter regime

N=500, L=12, per-site mutation rate 2e-5, s1=0.005, s2 in {0.01,0.02,0.04,0.08,0.16,0.32}, 10N resident relaxation generations, 1,000 adaptive replicates per condition.

The direct validation used seed `20260823`. Relaxed resident states were reused across s2 values as a common-random-numbers variance-reduction device; each condition's marginal distribution is unchanged.

The adaptive run stops when resident phenotype p0 first falls below 25% of the population and records the dominant adaptive phenotype. The manuscript treats this threshold-based takeover outcome as a computational proxy for which adaptive phenotype fixes first.


## Burn-in transition audit

The public Martin et al. fixation implementation was checked after the three proofreading passes. During the resident-only relaxation, p0 has fitness 1 and p1/p2 have fitness 0. Mutants outside p0 that are created in the final relaxation generation remain in the population array, but their fitness is zero and they therefore have zero probability of being selected as parents in the first adaptive generation. The count-level validation runner removes those zero-weight individuals before that parent-selection draw. These two implementations induce the same distribution for the first adaptive offspring generation.

Public source audited: `evolution_functions/evolutionary_dynamics_function_fixation_numba.py` in the Martin et al. repository.

## Analytic models

Run:

```powershell
.\scripts\RUN_ANALYTIC_FROM_POWERSHELL.ps1
```

This reconstructs the neutral component, computes the average-rate baseline, recomputes the Martin et al. (2024) burst-aware independent two-peak approximation from its public formula, and computes the state-resolved joint killed-Markov prediction.

## Wright-Fisher reference

The exact run that generated `results/reference/final_summary.json` was performed in the original experiment workspace before this repository cleanup. The historical runner is retained for auditability. The repository-native runner is provided for reruns, but it resumes only after complete relaxation or complete s2 conditions; it does not checkpoint individual replicates.

This limitation is intentional: the repository should not imply that the refactored long-run interface has been independently revalidated against the frozen 1000x6 reference when it has not.

## Repository-native full rerun

```powershell
.\scripts\RUN_FULL_FROM_POWERSHELL.ps1
```

A 20-replicate smoke test is available as `RUN_QUICK_CHECK_FROM_POWERSHELL.ps1`. The frozen 1000x6 reference was produced by the historical runner before repository refactoring; the repository-native runner preserves the same count-level update logic but has only coarse stage-level resume and should be compared against the frozen reference after any future code change.
