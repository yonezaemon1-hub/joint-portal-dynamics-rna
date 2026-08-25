#!/usr/bin/env python3
"""Summarize a completed Wright-Fisher threshold-takeover benchmark against all analytic models."""
import argparse,json
from pathlib import Path
import numpy as np
import pandas as pd

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--wf-json',required=True); ap.add_argument('--analytic-json',required=True); ap.add_argument('--outdir',default='results'); args=ap.parse_args()
    wf=json.loads(Path(args.wf_json).read_text(encoding='utf-8')); an=json.loads(Path(args.analytic_json).read_text(encoding='utf-8'))
    amap={float(r['s2']):r for r in an['results']}; rows=[]
    for r in wf['results']:
        s=float(r['s2']); a=amap[s]; y=float(r.get('wf_p2_takeover_proxy', r['wf_p2_first']))
        row={'s2':s,'WF_p2_takeover_proxy':y,'WF_p2_first':y,'average_rate_independent':a['average_rate_p2_first'],'Martin2024_burst_aware_independent':a['Martin2024_burst_aware_p2_first'],'joint_killed_Markov':a['joint_p2_first']}
        for k in ['average_rate_independent','Martin2024_burst_aware_independent','joint_killed_Markov']: row['abs_error_'+k]=abs(row[k]-y)
        rows.append(row)
    df=pd.DataFrame(rows); out=Path(args.outdir); out.mkdir(exist_ok=True,parents=True); df.to_csv(out/'comparison.csv',index=False)
    maes={k:float(df['abs_error_'+k].mean()) for k in ['average_rate_independent','Martin2024_burst_aware_independent','joint_killed_Markov']}
    summary={'MAE':maes,'joint_error_reduction_vs_average_rate':1-maes['joint_killed_Markov']/maes['average_rate_independent'],'joint_error_reduction_vs_burst_aware':1-maes['joint_killed_Markov']/maes['Martin2024_burst_aware_independent'],'joint_closer_than_burst_aware_conditions':int(np.sum(df['abs_error_joint_killed_Markov']<df['abs_error_Martin2024_burst_aware_independent']))}
    (out/'comparison_summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8'); print(json.dumps(summary,indent=2))
if __name__=='__main__': main()
