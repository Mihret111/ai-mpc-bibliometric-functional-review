"""critical-review set:
    per-front top by cites/year, plus era-history picks (2000-09 top 8, 2010-16 top 10 by cites), plus 8 top reviews. """
from common import load
import pandas as pd, re, itertools
from collections import Counter, defaultdict
import networkx as nx
df,c=load('master_corpus_v2.csv.gz')
sub=c[c['wos_cr'].notna()&c['year'].between(2021,2025)&c['doctype'].isin(['article','review'])].copy()
def refkey(s):
    p=[x.strip() for x in str(s).split(',')]
    if len(p)<3: return None
    a=re.sub(r'[^a-z ]','',p[0].lower()).strip(); y=p[1].strip()
    return f'{a},{y},{p[2].strip().lower()[:20]}' if a and y.isdigit() else None
sub['rset']=sub['wos_cr'].map(lambda s:{k for k in (refkey(x) for x in str(s).split(';')) if k})
sub=sub[sub['rset'].map(len)>=10]
inv=defaultdict(list)
for i,rs in zip(sub.index,sub['rset']):
    for r in rs: inv[r].append(i)
pair=Counter()
for r,d in inv.items():
    if 2<=len(d)<=150:
        for a,b in itertools.combinations(d,2): pair[(a,b)]+=1
G=nx.Graph(); G.add_weighted_edges_from((a,b,w) for (a,b),w in pair.items() if w>=8)
comms=[x for x in nx.community.greedy_modularity_communities(G,weight='weight') if len(x)>=40]
front={j:i+1 for i,x in enumerate(comms) for j in x}
c['front']=pd.Series(front); c['cpy']=c['cites']/(2026-c['year']).clip(lower=1)
prim=c[c['doctype']!='review']; sel=[]
for f in sorted(c['front'].dropna().unique()):
    sel+=list(prim[prim['front']==f].nlargest(8 if f<=6 else 4,'cpy').index)
sel+=list(prim[prim['year'].between(2000,2009)].nlargest(8,'cites').index)
sel+=list(prim[prim['year'].between(2010,2016)].nlargest(10,'cites').index)
sel+=list(c[c['doctype']=='review'].nlargest(8,'cpy').index)
sel=list(dict.fromkeys(sel))
R=c.loc[sel,['title','year','source','doctype','cites','front']].copy()
R['cites_per_year']=c.loc[sel,'cpy'].round(1)
print(f'candidates: {len(R)} | eras 2000s {(R["year"]<2010).sum()} / 2010s {R["year"].between(2010,2019).sum()} / 2020s {(R["year"]>=2020).sum()}')
R.sort_values(['front','cites_per_year'],ascending=[True,False]).to_csv('outputs/review_set_candidates.csv',index=False)
