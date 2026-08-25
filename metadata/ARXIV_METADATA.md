# arXiv submission metadata

- Primary category: q-bio.PE (Populations and Evolution)
- Title: Joint Portal Dynamics on an RNA Neutral Network Improve Prediction of Competing Adaptive Fixations
- Authors: Ryutaro Yonezu
- Comments: 8 pages, 2 figures; computational preprint; Zenodo preprint DOI 10.5281/zenodo.22095413; code and frozen reference results available in the associated GitHub repository; archived software release DOI 10.5281/zenodo.22095082.
- License suggestion: arXiv's non-exclusive license to distribute (review the current arXiv license choices at submission).

## Abstract

Models of mutation-limited adaptation can fail when access to competing adaptive phenotypes is structured on the same neutral genotype network. Martin et al. (2024) showed that phenotype arrivals can be bursty and developed a burst-aware approximation for competing peaks, while explicitly identifying dependence between multiple phenotype-introduction processes as a remaining problem. Here we represent neutral motion and all successful adaptive exits as one state-resolved killed continuous-time Markov process. The mathematics is standard; the contribution tested is the joint application to competing phenotype portals on a shared RNA neutral network. In the published focal two-peak RNA system, our ViennaRNA 2.7.2 reconstruction contains 1,937 resident genotypes and 13,355 neutral edges, with 517 portal edges to the frequent adaptive phenotype p1 and 16 to the rarer phenotype p2, and zero portal-genotype overlap. Under N=500, per-site mutation rate 2 x 10^-5, s1=0.005, and six s2 values, we compared three analytic predictions with a direct count-level Wright-Fisher re-execution of 1,000 replicates per condition. Mean absolute error (MAE) was 0.2220 for the simple average-rate independent model, 0.0349 for the Martin et al. burst-aware independent model, and 0.01256 for the joint killed-Markov model. Thus the joint model reduced MAE by 64.0% relative to the stronger burst-aware independent baseline and by 94.3% relative to the average-rate baseline. It was closer than the burst-aware model in 5/6 conditions and closer than the average-rate model in 6/6. The result supports a narrow conclusion: when competing adaptive opportunities are exposed along the same structured neutral trajectory, retaining shared state information can materially improve prediction of the p2-first outcome, benchmarked here by a threshold-based Wright-Fisher takeover proxy, beyond models that combine phenotype-specific marginal statistics independently.

## Files

Upload `Joint_Portal_Dynamics_RNA_Preprint_Final_v1_2.pdf`. This PDF was generated from DOCX, not TeX. Preprint v1.2 contains the permanent GitHub repository, Zenodo preprint DOI 10.5281/zenodo.22095413, and Zenodo software DOI 10.5281/zenodo.22095082; the scientific results and numerical values are unchanged from v1.1.

First-time submission to a q-bio endorsement domain may require endorsement.
