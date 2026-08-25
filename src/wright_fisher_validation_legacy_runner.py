#!/usr/bin/env python3
"""
JOINT_PORTAL_RNA_WRIGHT_FISHER_VALIDATION_V1

Historical direct Wright–Fisher re-execution on the reconstructed RNA GP map, using the
published Fig. 7 parameter regime:
  N=500, per-site mu=2e-5, s1=0.005,
  s2=[0.01,0.02,0.04,0.08,0.16,0.32],
  1000 replicates, 10*N generations of pre-adaptation relaxation.

The stopping event (resident p0 below 25%, then dominant phenotype recorded) is
a threshold-based takeover proxy for which adaptive phenotype fixes first.

The update is mathematically equivalent at genotype-count level to sampling N
offspring independently from fitness-weighted parents, followed by independent
per-site mutations. Multiple-site mutations are retained exactly via a
conditional Hamming-distance sampler.

This script uses ViennaRNA only for phenotypes of genuinely new mutated
genotypes. It reuses the fold cache produced by the earlier RNA experiment.

It compares:
  (A) independent-arrival prediction
  (B) joint Markov prediction from martin2024_joint_portal_N500_result.json
  (C) direct Wright–Fisher re-execution

Claim boundary:
  computational only; no wet lab; no new mathematics claimed.
"""

import argparse, json, math, os, sys, time
from collections import Counter
from pathlib import Path
import numpy as np

try:
    import RNA
except ImportError as e:
    raise SystemExit("ViennaRNA import failed. Run from the existing .venv_windows.") from e

RNA.cvar.uniq_ML = 1

BASES = "ACUG"
DB_TO_BIN = {".":"00","(":"10",")":"01","_":"00","[":"10","]":"01"}
L = 12
K = 4

def dotbracket_to_int(db):
    return int("1" + "".join(DB_TO_BIN[c] for c in db), 2)

def _subopt_to_dict(structure, energy, data):
    if structure is not None:
        data[structure] = energy

def fold_int(seq):
    fc = RNA.fold_compound(seq)
    mfe_structure, mfe = fc.mfe()
    d = {}
    fc.subopt_cb(int(0.11*100), _subopt_to_dict, d)
    alternatives = [
        s for s in d
        if s != mfe_structure and abs(fc.eval_structure(s)-mfe) < 0.01
    ]
    if alternatives:
        return dotbracket_to_int(".")
    return dotbracket_to_int(mfe_structure)

class PhenotypeCache:
    def __init__(self, path):
        self.path = Path(path)
        if not self.path.exists():
            raise FileNotFoundError(f"fold cache missing: {self.path}")
        raw = json.loads(self.path.read_text(encoding="utf-8"))
        self.d = {str(k): int(v) for k,v in raw.items()}
        self.new = 0

    def get(self, seq):
        v = self.d.get(seq)
        if v is None:
            v = int(fold_int(seq))
            self.d[seq] = v
            self.new += 1
        return v

    def save(self):
        tmp = self.path.with_suffix(".tmp")
        tmp.write_text(json.dumps(self.d), encoding="utf-8")
        tmp.replace(self.path)

def mutate_one(seq, cat):
    # cat in [0,35]: site × one of the 3 alternative bases.
    pos = cat // 3
    alt_index = cat % 3
    old = seq[pos]
    alts = [b for b in BASES if b != old]
    return seq[:pos] + alts[alt_index] + seq[pos+1:]

def mutation_count_weights(mu):
    # Exact probability of Hamming distance d after independent site mutations.
    w = np.array([
        math.comb(L,d) * (mu**d) * ((1-mu)**(L-d))
        for d in range(L+1)
    ], dtype=float)
    w /= w.sum()
    return w

def mutate_multi(seq, d, rng):
    positions = rng.choice(L, size=d, replace=False)
    s = list(seq)
    for pos in positions:
        alts = [b for b in BASES if b != s[pos]]
        s[pos] = alts[int(rng.integers(0,3))]
    return "".join(s)

def reproduce_counts(pop, phenotype_cache, fitness_map, N, mu, rng, hdist_w):
    # Exact Wright–Fisher parent selection at genotype-count level.
    live = []
    weights = []
    for seq, count in pop.items():
        ph = phenotype_cache.get(seq)
        fit = fitness_map.get(ph, 0.0)
        if fit > 0 and count > 0:
            live.append(seq)
            weights.append(count * fit)
    if not weights or sum(weights) <= 0:
        return Counter()

    probs = np.asarray(weights, float)
    probs /= probs.sum()
    parent_counts = rng.multinomial(N, probs)

    out = Counter()
    q0 = hdist_w[0]
    q1 = hdist_w[1]
    qmulti = float(hdist_w[2:].sum())

    for seq, n in zip(live, parent_counts):
        n = int(n)
        if n <= 0:
            continue
        n0, n1, nm = rng.multinomial(n, [q0, q1, qmulti])
        if n0:
            out[seq] += int(n0)

        if n1:
            # Exactly one changed site; all 36 point substitutions equiprobable.
            cats = rng.multinomial(int(n1), np.full(36, 1/36))
            for cat, c in enumerate(cats):
                if c:
                    m = mutate_one(seq, cat)
                    phenotype_cache.get(m)
                    out[m] += int(c)

        if nm:
            cond = hdist_w[2:] / qmulti
            ds = rng.choice(np.arange(2,L+1), size=int(nm), p=cond)
            for d in ds:
                m = mutate_multi(seq, int(d), rng)
                phenotype_cache.get(m)
                out[m] += 1

    if sum(out.values()) != N:
        raise RuntimeError("offspring count mismatch")
    return out

def phenotype_counts(pop, cache):
    c = Counter()
    for seq,n in pop.items():
        c[cache.get(seq)] += int(n)
    return c

def relax_one(start_seq, cache, p0, N, mu, rng, hdist_w, generations):
    pop = Counter({start_seq:N})
    fit = {p0:1.0}
    for _ in range(generations):
        pop = reproduce_counts(pop, cache, fit, N, mu, rng, hdist_w)
        # Equivalent to the paper's transition into the adaptive phase:
        # non-p0 individuals present in the final relaxation generation have
        # fitness zero for the first adaptive parent-selection step.
    return Counter({seq:n for seq,n in pop.items() if cache.get(seq)==p0})

def adaptive_one(relaxed_p0_pop, cache, p0,p1,p2,s1,s2,N,mu,rng,hdist_w,T):
    pop = relaxed_p0_pop.copy()
    fit = {p0:1.0, p1:1.0+s1, p2:1.0+s2}

    for step in range(T):
        pop = reproduce_counts(pop, cache, fit, N, mu, rng, hdist_w)
        pc = phenotype_counts(pop, cache)
        if pc.get(p0,0) < 0.25*N:
            if not pc:
                return -1, step
            winner = max(pc.items(), key=lambda kv: kv[1])[0]
            return int(winner), step
    return -1, T

def wilson(k,n,z=1.959963984540054):
    if n == 0:
        return [None,None]
    p=k/n
    den=1+z*z/n
    cen=(p+z*z/(2*n))/den
    half=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/den
    return [cen-half, cen+half]

def load_joint(path):
    d=json.loads(Path(path).read_text(encoding="utf-8"))
    if int(d["inputs"]["N"]) != 500:
        raise RuntimeError("joint result is not N=500")
    return {float(r["s2"]):r for r in d["results"]}

def run(args):
    root=Path(args.experiment_dir).resolve()
    cache=PhenotypeCache(root/"rna_fold_cache_martin2024.json")
    joint=load_joint(root/"martin2024_joint_portal_N500_result.json")

    p0,p1,p2=19529749,27262981,27918661
    start="ACCUAAAAAAGG"
    if cache.get(start)!=p0:
        raise RuntimeError("start phenotype mismatch")

    p0_nodes=sorted([s for s,ph in cache.d.items() if int(ph)==p0])
    if len(p0_nodes)!=1937:
        raise RuntimeError(f"expected 1937 p0 NC nodes from validated cache, got {len(p0_nodes)}")

    N=500
    mu=2e-5
    s1=0.005
    s2s=[0.01,0.02,0.04,0.08,0.16,0.32]
    reps=args.reps
    relax_gens=10*N
    T=10_000_000
    hdist_w=mutation_count_weights(mu)

    expected_mutants=N*L*mu
    print(f"PRECHECK p0_nodes={len(p0_nodes)} ViennaRNA={getattr(RNA,'__version__','unknown')}")
    print(f"PRECHECK N={N} mu={mu} E[site mutations/generation]={expected_mutants:.6f}")
    print(f"PRECHECK P(>=2 substitutions/offspring)={hdist_w[2:].sum():.12g}")

    relaxed_file=root/f"wf_relaxed_N500_mu2e-5_reps{reps}_seed{args.seed}.json"
    if relaxed_file.exists() and not args.force_relax:
        raw=json.loads(relaxed_file.read_text(encoding="utf-8"))
        relaxed=[Counter({k:int(v) for k,v in d.items()}) for d in raw]
        if len(relaxed)!=reps:
            raise RuntimeError("relaxed checkpoint count mismatch")
        print(f"RELAX resume {len(relaxed)} states")
    else:
        relaxed=[]
        ss=np.random.SeedSequence(args.seed)
        child_seeds=ss.spawn(reps)
        for i in range(reps):
            rng=np.random.default_rng(child_seeds[i])
            start_seq=p0_nodes[int(rng.integers(0,len(p0_nodes)))]
            state=relax_one(start_seq,cache,p0,N,mu,rng,hdist_w,relax_gens)
            relaxed.append(state)
            if (i+1)%50==0 or i==0:
                print(f"RELAX {i+1}/{reps} cache_new={cache.new}", flush=True)
                cache.save()
        relaxed_file.write_text(json.dumps([dict(x) for x in relaxed]),encoding="utf-8")
        cache.save()

    results=[]
    for ci,s2 in enumerate(s2s):
        ck=root/f"wf_condition_s2_{str(s2).replace('.','p')}_reps{reps}_seed{args.seed}.json"
        if ck.exists() and not args.force_conditions:
            r=json.loads(ck.read_text(encoding="utf-8"))
            results.append(r)
            print(f"CONDITION s2={s2} resumed")
            continue

        wins=[]
        times=[]
        ss=np.random.SeedSequence([args.seed, 1000+ci])
        seeds=ss.spawn(reps)
        for i in range(reps):
            rng=np.random.default_rng(seeds[i])
            winner,t=adaptive_one(relaxed[i],cache,p0,p1,p2,s1,s2,N,mu,rng,hdist_w,T)
            wins.append(int(winner))
            times.append(int(t))
            if (i+1)%50==0 or i==0:
                p2wins=sum(1 for w in wins if w==p2)
                succ=sum(1 for w in wins if w in (p1,p2))
                print(f"S2={s2:.3f} {i+1}/{reps} p2={p2wins}/{succ} cache_new={cache.new}",flush=True)
                cache.save()

        succ=sum(1 for w in wins if w in (p1,p2))
        p2wins=sum(1 for w in wins if w==p2)
        p2prob=p2wins/succ if succ else float("nan")
        jr=joint[s2]
        r={
            "s2":s2,
            "reps":reps,
            "successful_p1_or_p2":succ,
            "p1_wins":sum(1 for w in wins if w==p1),
            "p2_wins":p2wins,
            "other_or_timeout":reps-succ,
            "wf_p2_first":p2prob,
            "wf_p2_first_wilson95":wilson(p2wins,succ),
            "mean_fixation_step_success":float(np.mean([t for w,t in zip(wins,times) if w in (p1,p2)])) if succ else None,
            "independent_p2_first":float(jr["independent"]["p2_first"]),
            "joint_markov_p2_first":float(jr["joint_markov"]["p2_first"]),
            "abs_error_independent_vs_wf":abs(float(jr["independent"]["p2_first"])-p2prob) if succ else None,
            "abs_error_joint_vs_wf":abs(float(jr["joint_markov"]["p2_first"])-p2prob) if succ else None,
        }
        ck.write_text(json.dumps(r,indent=2),encoding="utf-8")
        results.append(r)
        cache.save()

    mae_ind=float(np.mean([r["abs_error_independent_vs_wf"] for r in results]))
    mae_joint=float(np.mean([r["abs_error_joint_vs_wf"] for r in results]))
    final={
        "experiment":"JOINT_PORTAL_RNA_WRIGHT_FISHER_VALIDATION_V1",
        "status":"EXPERIMENT_COMPLETE",
        "claim_boundary":{
            "computational":True,
            "wet_lab":False,
            "new_mathematics_claimed":False,
            "published_parameter_regime":True,
            "count_level_WF_equivalence":"fitness-weighted multinomial parents + exact independent per-site mutation distribution",
            "relaxed_states_reused_across_s2":"common-random-numbers variance reduction; marginal distribution unchanged"
        },
        "environment":{
            "python":sys.version.split()[0],
            "ViennaRNA":getattr(RNA,"__version__","unknown")
        },
        "parameters":{
            "N":N,"mu_per_site":mu,"L":L,"s1":s1,"s2":s2s,
            "reps":reps,"relax_generations":relax_gens,"T_cap":T,
            "seed":args.seed,"p0_nodes":len(p0_nodes)
        },
        "results":results,
        "summary":{
            "mae_independent_vs_WF":mae_ind,
            "mae_joint_markov_vs_WF":mae_joint,
            "joint_error_reduction_fraction":1-mae_joint/mae_ind if mae_ind>0 else None,
            "independent_to_joint_mae_ratio":mae_ind/mae_joint if mae_joint>0 else None,
            "conditions_joint_better":sum(r["abs_error_joint_vs_wf"]<r["abs_error_independent_vs_wf"] for r in results),
            "conditions_total":len(results),
        }
    }
    out=root/f"martin2024_WF_direct_reps{reps}_result.json"
    out.write_text(json.dumps(final,indent=2),encoding="utf-8")
    cache.save()

    print("\n=== FINAL DIRECT WF COMPARISON ===")
    for r in results:
        print(
            f"s2={r['s2']:.3f} WF={r['wf_p2_first']:.5f} "
            f"CI=[{r['wf_p2_first_wilson95'][0]:.5f},{r['wf_p2_first_wilson95'][1]:.5f}] "
            f"IND={r['independent_p2_first']:.5f} "
            f"JOINT={r['joint_markov_p2_first']:.5f}"
        )
    print(f"MAE independent={mae_ind:.8f}")
    print(f"MAE joint={mae_joint:.8f}")
    print(f"JOINT_ERROR_REDUCTION={final['summary']['joint_error_reduction_fraction']:.6f}")
    print(f"JOINT_BETTER={final['summary']['conditions_joint_better']}/{len(results)}")
    print("FINAL=PASS_WRIGHT_FISHER_DIRECT_COMPARISON_COMPLETE")
    print(f"RESULT_JSON={out}")

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--experiment-dir",required=True)
    ap.add_argument("--reps",type=int,default=1000)
    ap.add_argument("--seed",type=int,default=20260823)
    ap.add_argument("--force-relax",action="store_true")
    ap.add_argument("--force-conditions",action="store_true")
    args=ap.parse_args()
    run(args)

if __name__=="__main__":
    main()
