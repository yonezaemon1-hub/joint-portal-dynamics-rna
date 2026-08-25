"""RNA GP-map helpers for the focal Martin et al. (2024) two-peak system."""
import json
from collections import deque
from pathlib import Path
import numpy as np
from scipy import sparse
import RNA

BASES = "ACUG"
DB_TO_BIN = {".":"00","(":"10",")":"01","_":"00","[":"10","]":"01"}
RNA.cvar.uniq_ML = 1

def dotbracket_to_int(db):
    return int("1"+"".join(DB_TO_BIN[c] for c in db),2)

def int_to_dotbracket(x):
    inv={"10":"(","00":".","01":")"}
    bits=bin(int(x))[3:]
    return "".join(inv[bits[i:i+2]] for i in range(0,len(bits),2))

def _subopt_cb(structure, energy, data):
    if structure is not None: data[structure]=energy

def fold_int(seq):
    fc=RNA.fold_compound(seq)
    mfe_structure,mfe=fc.mfe()
    d={}; fc.subopt_cb(int(0.11*100),_subopt_cb,d)
    alternatives=[s for s in d if s!=mfe_structure and abs(fc.eval_structure(s)-mfe)<0.01]
    return dotbracket_to_int("." if alternatives else mfe_structure)

def one_mutants(seq):
    for i,old in enumerate(seq):
        for b in BASES:
            if b!=old: yield seq[:i]+b+seq[i+1:]

class FoldCache:
    def __init__(self,path):
        self.path=Path(path); self.d={}
        if self.path.exists(): self.d={str(k):int(v) for k,v in json.loads(self.path.read_text(encoding='utf-8')).items()}
    def get(self,seq):
        if seq not in self.d: self.d[seq]=int(fold_int(seq))
        return int(self.d[seq])
    def save(self): self.path.write_text(json.dumps(self.d),encoding='utf-8')

def build_nc(start_seq,p0,targets,cache):
    if cache.get(start_seq)!=p0: raise RuntimeError('Published start phenotype mismatch.')
    q=deque([start_seq]); seen={start_seq}; edges=set(); local={int(t):{} for t in targets}
    while q:
        g=q.popleft(); counts={int(t):0 for t in targets}
        for m in one_mutants(g):
            pm=cache.get(m)
            if pm==p0:
                edges.add(tuple(sorted((g,m))))
                if m not in seen: seen.add(m); q.append(m)
            elif pm in counts: counts[pm]+=1
        for t in targets: local[int(t)][g]=counts[int(t)]
    nodes=sorted(seen); idx={g:i for i,g in enumerate(nodes)}
    rows=[]; cols=[]; data=[]; deg=np.zeros(len(nodes))
    for g,h in edges:
        i,j=idx[g],idx[h]; rows += [i,j]; cols += [j,i]; data += [1.,1.]; deg[i]+=1; deg[j]+=1
    L=sparse.csr_matrix((data,(rows,cols)),shape=(len(nodes),len(nodes)))-sparse.diags(deg)
    portals={int(t):np.array([local[int(t)][g] for g in nodes],float) for t in targets}
    return nodes,L,portals,{'neutral_nodes':len(nodes),'neutral_edges':len(edges),'mean_neutral_degree':float(deg.mean())}
