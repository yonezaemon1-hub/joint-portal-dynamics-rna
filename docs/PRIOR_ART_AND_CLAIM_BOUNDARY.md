# Prior art and claim boundary

## Existing foundations

1. **Origin-fixation / mutation-limited evolution**: McCandlish & Stoltzfus (2014).
2. **First-passage / findability in weak-mutation evolution**: McCandlish (2013).
3. **Markov-chain treatment of weak-mutation evolution on arbitrary fitness landscapes**: McCandlish (2018).
4. **Neutral-network topology and dynamics**: Aguirre, Buldu & Manrubia (2009).
5. **Non-neutral genetic correlations and local phenotype-access heterogeneity**: Greenbury et al. (2016).
6. **Hierarchical community structure of RNA neutral components**: Weiss & Ahnert (2020).
7. **Arrival of the frequent and portal-limited/bursty phenotype introduction**: Schaper & Louis (2014); Martin et al. (2024).
8. **Genotype-level partitioned absorbing-state calculations**: Rozhoňová et al. (2024) replace transitions entering a target genotype set by absorbing states, split them into B1/B2 classes, and calculate the probability of absorption through a specified transition class.
9. **Absorbing/killed Markov and first-passage mathematics**: standard; no novelty claimed here.

## Close methodological precedent: Rozhoňová et al. (2024)

Rozhoňová et al. analyze empirical adaptive landscapes under rewired genetic codes using standard Markov-chain theory. Their method replaces each mutation entering a target genotype set with a corresponding absorbing state, partitions those absorbing states into **B1** (transitions of interest) and **B2** (other transitions), and calculates the probability of absorption through B1. This is a close methodological precedent for genotype-level partitioned absorbing-state calculations, but it does not itself address Martin et al.'s phenotype-portal dependence problem.

Accordingly, this project does **not** claim novelty for:

- using an absorbing or killed Markov chain on a genotype landscape;
- representing alternative transitions by multiple absorbing channels; or
- calculating probabilities of different absorption routes.

The distinction is application-specific: Rozhoňová et al. study accessibility and evolvability under rewired genetic codes, whereas the present work tests dependence between **phenotype-specific adaptive portal processes encountered along one shared neutral RNA trajectory**, in the Martin et al. two-peak setting.

## Martin et al. (2024) boundary

Martin et al. already derive a burst-aware approximation for competing adaptive peaks. Their multi-phenotype calculation combines phenotype-specific fixation-time distributions under an independence assumption, and their discussion explicitly notes that introduction processes may be dependent when access to different phenotypes is structured on the same neutral component. They identify analytical/computational treatment of that dependence as future work.

## Narrow residual addressed here

The tested residual is **not** “portals matter,” “bursts matter,” “Markov chains can model evolution,” or “competing absorption can be computed.” It is:

> Whether retaining the shared resident-genotype state while representing multiple competing phenotype-specific portal exits as one state-resolved killed process improves prediction of the p2-first outcome over the Martin et al. burst-aware independent competition model in the focal RNA two-peak setting. The direct Wright-Fisher benchmark uses a threshold-based takeover outcome (resident p0 below 25%) as a proxy for which adaptive phenotype fixes first.

The direct 1000x6 Wright-Fisher benchmark supports that residual: MAE 0.03489 for the Martin burst-aware independent approximation versus 0.01256 for the joint model (about 64.0% lower); the joint model is closer in 5/6 conditions.

## Search status

A targeted literature **re-audit through 25 August 2026** identified close methodological precedents, including Rozhoňová et al. (2024), but did not identify a publication that directly combines all of the following in the focal Martin et al. RNA two-peak setting:

1. portal-limited multi-phenotype competition;
2. one shared resident-genotype state / neutral trajectory;
3. competing phenotype-specific successful-exit hazards;
4. fixation-order prediction;
5. comparison against the Martin burst-aware independent approximation; and
6. direct threshold-based Wright-Fisher takeover benchmarking.

This is a **to-our-knowledge** statement, not proof of absence.

## Key references

- Martin NS, Schaper S, Camargo CQ, Louis AA. Molecular Biology and Evolution 41(6):msae085 (2024). DOI: 10.1093/molbev/msae085.
- Rozhoňová H, Martí-Gómez C, McCandlish DM, Payne JL. PLoS Biology 22(5):e3002594 (2024). DOI: 10.1371/journal.pbio.3002594.
- McCandlish DM. Evolution 67:2592-2603 (2013). DOI: 10.1111/evo.12128.
- McCandlish DM. Heredity 121:449-465 (2018). DOI: 10.1038/s41437-018-0142-6.
- Greenbury SF, Schaper S, Ahnert SE, Louis AA. PLoS Comput Biol 12:e1004773 (2016). DOI: 10.1371/journal.pcbi.1004773.
- Aguirre J, Buldu JM, Manrubia SC. Phys Rev E 80:066112 (2009). DOI: 10.1103/PhysRevE.80.066112.
- Weiss M, Ahnert SE. J R Soc Interface 17:20200608 (2020). DOI: 10.1098/rsif.2020.0608.
