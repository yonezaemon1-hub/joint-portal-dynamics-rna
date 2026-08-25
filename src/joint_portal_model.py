#!/usr/bin/env python3
"""Compute average-rate, Martin-2024 burst-aware, and joint killed-Markov predictions."""
import argparse, json, math, sys
from pathlib import Path
import numpy as np
from scipy import sparse
from scipy.sparse.linalg import spsolve
from rna_gp import FoldCache, build_nc, int_to_dotbracket

START='ACCUAAAAAAGG'; P0=19529749; P1=27262981; P2=27918661
N=500; MU=2e-5; LENGTH=12; ALPHABET=4; S1=0.005
S2=[0.01,0.02,0.04,0.08,0.16,0.32]

def pfix(s,N=N): return (1-math.exp(-2*s))/(1-math.exp(-2*N*s))

def solve_joint(L,kappas,alpha):
    A=(-(L-sparse.diags(np.sum(np.stack(kappas),axis=0)))).tocsr()
    probs=[]
    for k in kappas: probs.append(float(alpha @ spsolve(A,k)))
    return probs

def martin_bursty_fixation_time(s,cpq,rho):
    # Reimplementation of the public Martin et al. (2024) burst-time expression,
    # including their polymorphic correction.
    pf=pfix(s)
    f=math.sqrt(1/(1+2*N*(1-MU*LENGTH*(1-rho))*MU*LENGTH*rho))
    t_neutral=1/(MU*LENGTH*rho)
    pfix_burst=(1+(ALPHABET-1)*rho*LENGTH/(N*f*pf))**-1
    t_app_burst=t_neutral/(cpq*LENGTH*(ALPHABET-1))
    t_burst=t_app_burst/pfix_burst
    t_app_poly=(cpq*LENGTH*N*(1-f)*MU)**-1
    t_poly=t_app_poly/pf
    return 1/(1/t_burst+1/t_poly)

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--workdir',default='.'); args=ap.parse_args()
    root=Path(args.workdir).resolve(); (root/'results').mkdir(exist_ok=True)
    cache=FoldCache(root/'results'/'rna_fold_cache.json')
    nodes,Q,portals,meta=build_nc(START,P0,[P1,P2],cache); cache.save()
    (root/'results'/'nc_nodes.json').write_text(json.dumps(nodes),encoding='utf-8')
    if len(nodes)!=1937: raise RuntimeError(f'Compatibility check failed: expected 1937 nodes, got {len(nodes)}')
    v1,v2=portals[P1],portals[P2]; alpha=np.ones(len(nodes))/len(nodes)
    rho=meta['mean_neutral_degree']/(LENGTH*(ALPHABET-1))
    phi1=float(v1.sum()/(len(nodes)*LENGTH*(ALPHABET-1))); phi2=float(v2.sum()/(len(nodes)*LENGTH*(ALPHABET-1)))
    t1=martin_bursty_fixation_time(S1,phi1,rho)
    out=[]
    for s2 in S2:
        k1=v1*N*pfix(S1); k2=v2*N*pfix(s2)
        jp=solve_joint(Q,[k1,k2],alpha)[1]
        lam1=float(alpha@k1); lam2=float(alpha@k2); avg=lam2/(lam1+lam2)
        t2=martin_bursty_fixation_time(s2,phi2,rho); burst=1/(1+t2/t1)
        out.append({'s2':s2,'average_rate_p2_first':avg,'Martin2024_burst_aware_p2_first':burst,'joint_p2_first':jp})
    payload={'environment':{'python':sys.version.split()[0]},'parameters':{'N':N,'mu':MU,'s1':S1,'s2':S2},'graph':meta,'portals':{'p1_edges':int(v1.sum()),'p2_edges':int(v2.sum()),'overlap':int(np.sum((v1>0)&(v2>0))),'phi1':phi1,'phi2':phi2,'rho':rho},'results':out}
    path=root/'results'/'analytic_predictions_N500.json'; path.write_text(json.dumps(payload,indent=2),encoding='utf-8')
    print(json.dumps(payload,indent=2)); print(f'OUTPUT={path}')
if __name__=='__main__': main()
