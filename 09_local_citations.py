"""LOCAL citations - how often each influential record is cited by other corpus records"""
from common import load
import pandas as pd, re
def norm_s(s): return re.sub(r'\s+',' ', re.sub(r'[^a-z0-9 ]',' ', str(s).lower()))
df, c = load('master_corpus_v2.csv')
refs_raw = c['refs'].fillna('').str.lower(); refs_norm = refs_raw.map(norm_s)
cand = c[c['cites']>=30].copy()
cand['nt'] = cand['title'].map(lambda t: norm_s(t).strip())
cand = cand[cand['nt'].str.len()>=25]
cand['sn'] = cand['authors'].map(lambda a: str(a).split(',')[0].split(' ')[0].strip().lower())
cand['ys'] = cand['year'].astype(int).astype(str)
loc={}
for n,(idx,r) in enumerate(cand.iterrows()):
    if n%500==0: print(f'  {n}/{len(cand)}')
    m = refs_norm.str.contains(r['nt'], regex=False); citing=set()
    for j in m[m].index.difference([idx]):
        for seg in refs_raw.loc[j].split(';'):
            if r['nt'] in norm_s(seg) and r['ys'] in seg and (len(r['sn'])<3 or r['sn'] in seg):
                citing.add(j); break
    d=str(r['doi'])
    if d.startswith('10.'): citing |= set(refs_raw[refs_raw.str.contains(d,regex=False)].index.difference([idx]))
    loc[idx]=min(len(citing), int(r['cites']))
cand['local_cites']=pd.Series(loc)
assert (cand['local_cites']<=cand['cites']).all()
top=cand.nlargest(15,'local_cites')[['title','year','source','cites','local_cites']]
print(top.head(10).to_string(index=False)); top.to_csv('outputs/table_top_cited_LOCAL.csv', index=False)
