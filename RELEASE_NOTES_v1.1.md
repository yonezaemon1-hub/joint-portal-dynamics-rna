# v1.1.0 release notes

Public research release with prior-art boundary re-audited on 25 August 2026.

## Prior-art correction

- Added Rozhoňová et al. (2024), **Robust genetic codes enhance protein evolvability**, as a close methodological precedent for genotype-level partitioned absorbing-state calculations.
- Explicitly states that absorbing/killed Markov mathematics and partitioned absorbing-state calculations are **not** novel contributions of this work.
- Retains only the narrow Martin-2024-specific residual: shared resident-genotype state across competing adaptive portal processes, p2-first prediction, and comparison against both the burst-aware independent comparator and a threshold-based Wright-Fisher takeover benchmark.

## Frozen numerical result - unchanged

- Frozen Wright-Fisher benchmark: 1,000 replicates x 6 selection conditions
- N = 500, per-site mutation rate = 2e-5, s1 = 0.005
- Average-rate independent MAE: 0.22200386
- Martin et al. burst-aware independent MAE: 0.03488920
- Joint killed-Markov MAE: 0.01256231
- Error reduction vs stronger burst-aware baseline: 64.0%
- Joint closer than burst-aware baseline: 5/6 conditions
- Joint closer than average-rate baseline: 6/6 conditions

The scientific model and frozen numerical results are unchanged. The public-release scripts and documentation were corrected during final proofreading; these release-engineering changes do not alter the reported numerical results.

## Final three-pass release audit

- Corrected the Rozhoňová description to target-set entry through specified transition classes; no claim that those classes are phenotype-adaptive exits is required.
- Clarified that the direct Wright-Fisher benchmark is a threshold-based takeover proxy (p0 < 25%), not observation of literal complete fixation.
- Corrected GitHub publication integrity so checksums are regenerated after account-specific metadata is written.
- Clarified that the repository-native full runner has coarse stage-level resume, not per-replicate checkpointing.
