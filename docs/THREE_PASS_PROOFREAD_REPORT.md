# Three-pass proofreading and GitHub release audit

Date: 25 August 2026

## Pass 1 - claims, prior art, and wording

- Rechecked Martin et al. (2024): their multi-phenotype calculation assumes independent phenotype-introduction processes, and they explicitly identify analytical/computational treatment of dependence as future work.
- Rechecked Rozhoňová et al. (2024): they use an absorbing Markov construction in which mutations entering a target genotype set are represented by absorbing states partitioned into B1/B2 classes.
- Corrected wording that described the B1/B2 classes as “adaptive transition classes”; the safer description is specified transition classes into a target genotype set.
- Kept the claim boundary narrow: no novelty claim for Markov, first-passage, killed/absorbing processes, portal-limited bursts, or genotype-level partitioned absorption.
- Softened “the exact type of dependence setting” to the broader dependence problem identified by Martin et al.; the focal p1/p2 portal sets have zero genotype overlap.

## Pass 2 - equations, numbers, and benchmark semantics

- Recomputed all headline metrics from `results/reference/final_comparison_1000x6.csv` and `final_summary.json`. MAEs remain 0.22200386 (average-rate), 0.03488920 (Martin burst-aware), and 0.01256231 (joint).
- Reconfirmed 64.0% MAE reduction versus the burst-aware comparator, 94.3% versus average-rate, joint closer in 5/6 versus burst-aware and 6/6 versus average-rate, and Wilson-interval inclusion counts of 4/6, 2/6, and 1/6 respectively.
- Reconfirmed 1,937 neutral nodes, 13,355 neutral edges, mean degree 13.78936, 517 p1 portal edges, 16 p2 portal edges, and zero portal-genotype overlap.
- Clarified the direct Wright-Fisher benchmark: the runner stops when resident p0 first falls below 25% and records the dominant phenotype. The manuscript now labels this as a threshold-based takeover proxy for which adaptive phenotype fixes first rather than literal observation of complete fixation.
- No frozen numerical result was changed.
- Corrected two manuscript-table rounding typos at s2/s1=8: burst-aware 0.08747 -> 0.08746 and its absolute error 0.02247 -> 0.02246; the underlying CSV and aggregate metrics were already correct.
- Removed a mathematical notation collision: the neutral continuous-time generator is now `Q`, while `L=12` remains reserved for RNA sequence length.
- Narrowed the title from plural “RNA Neutral Networks” to singular “an RNA Neutral Network” to match the one-component evidence base.

## Pass 3 - GitHub reproducibility and release integrity

- Found and fixed a real release-integrity bug: the publication script wrote account-specific metadata after `SHA256SUMS.txt` had been generated, which would make hashes stale after publication.
- `PUBLISH_GITHUB_FROM_POWERSHELL.ps1` now resolves account metadata first, regenerates all SHA256 hashes, verifies them, and only then commits/pushes.
- Added `scripts/VERIFY_RELEASE_FROM_POWERSHELL.ps1` as a fail-closed release integrity gate.
- Corrected README/reproduction wording: the repository-native long runner has coarse stage-level resume, not per-replicate checkpointing, and has not been independently revalidated against the frozen 1000x6 reference after refactoring.
- Replaced externally ambiguous “certified” wording in public-facing reproduction text with “frozen reference run” / “historical runner” where appropriate.
- Confirmed the software license is MIT and the manuscript license is CC BY 4.0; removed the older contradictory note that no license had been selected.
- Updated both manuscript figures so the Wright-Fisher series and error axis explicitly say takeover proxy rather than literal fixation.
- Hardened publication packaging: generated rerun outputs are git-ignored, and the publication hash manifest is built from staged/tracked release files so ignored local artifacts cannot leak into `SHA256SUMS.txt`.

## Final scope

The final public package claims a narrow computational result only: retaining shared resident-genotype state in the focal Martin et al. RNA two-peak portal competition improves aggregate prediction relative to the published burst-aware independent comparator under the stated threshold-based Wright-Fisher benchmark. It does not claim new Markov mathematics or a new general law of evolution.
