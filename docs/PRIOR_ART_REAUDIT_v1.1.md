# Prior-art re-audit - v1.1

Date: 25 August 2026

## Trigger

The pre-release v1.0 package correctly stated that killed/absorbing Markov mathematics was standard, but it did not explicitly discuss the close genotype-landscape absorbing-chain precedent of Rozhoňová et al. (2024).

## Added precedent

Rozhoňová H, Martí-Gómez C, McCandlish DM, Payne JL. **Robust genetic codes enhance protein evolvability.** PLoS Biology. 2024;22(5):e3002594. DOI: 10.1371/journal.pbio.3002594.

Their analysis uses standard Markov-chain theory, replaces mutations entering a target genotype set with absorbing states, partitions those states into B1/B2 classes, and calculates the probability of absorption through the transition class of interest. This is a close mathematical precedent, not a prior solution of the Martin et al. portal-dependence question.

## Consequence for claim boundary

The v1.1 manuscript and repository now explicitly disclaim novelty for genotype-level absorbing-chain analysis and partitioned absorbing-state calculations. The retained narrow contribution is the Martin-2024-specific application: shared resident-genotype state across competing phenotype portal processes, evaluated by fixation-order prediction against the burst-aware independent comparator and a threshold-based Wright-Fisher takeover benchmark in the focal RNA two-peak system.

No numerical result or executable model was changed by this prior-art correction.
