"""Countries, institutions, collaboration"""
from common import load
import pandas as pd, re, itertools
from collections import Counter
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
import networkx as nx
df, c = load('master_corpus_v2.csv')
FIX={'peoples r china':'china','united states':'usa','u.s.a':'usa','england':'united kingdom','scotland':'united kingdom','wales':'united kingdom','north ireland':'united kingdom','republic of korea':'south korea','korea':'south korea','russian federation':'russia','viet nam':'vietnam','turkiye':'turkey'}
def countries(s):
    out=set()
    for a in str(s).split(';'):
        t=re.sub(r'\d+','',a.split(',')[-1].strip().lower().rstrip('.')).strip()
        if 2<len(t)<30: out.add(FIX.get(t,t))
    return out
c['ctry']=c['aff'].map(countries)
cnt=Counter(); [cnt.update(s) for s in c['ctry']]
print('top 12:'); [print(f'  {v:5d} ({100*v/len(c):4.1f}%)  {k.title()}') for k,v in cnt.most_common(12)]
print(f'MCP overall: {100*(c["ctry"].map(len)>=2).mean():.1f}%')
pairs=Counter()
for s in c['ctry']:
    for a,b in itertools.combinations(sorted(s),2): pairs[(a,b)]+=1
PAT=re.compile(r'univ|polytech|institut|college|academ|tech\b',re.I)
def insts(s):
    out=set()
    for seg in str(s).split(';'):
        hit=[p.strip() for p in seg.split(',') if PAT.search(p)]
        if hit: out.add(re.sub(r'\s+',' ',hit[0]).title()[:48])
    return out
inst=Counter(); [inst.update(insts(s)) for s in c['aff'].dropna()]
print('top institutions:'); [print(f'  {v:4d}  {k}') for k,v in inst.most_common(8)]
pd.DataFrame(cnt.most_common(30),columns=['country','records']).to_csv('outputs/table_top_countries.csv',index=False)
pd.DataFrame(inst.most_common(25),columns=['institution','records']).to_csv('outputs/table_top_institutions.csv',index=False)
G=nx.Graph(); top30={k for k,_ in cnt.most_common(30)}
G.add_weighted_edges_from((a,b,w) for (a,b),w in pairs.items() if w>=15 and a in top30 and b in top30)
pos=nx.spring_layout(G,k=.8,seed=3,weight='weight')
fig,ax=plt.subplots(figsize=(10,7.5),dpi=150)
nx.draw_networkx_edges(G,pos,alpha=.25,width=[G[u][v]['weight']/60 for u,v in G.edges()],ax=ax)
nx.draw_networkx_nodes(G,pos,node_size=[cnt[n]/6 for n in G.nodes()],node_color='#2a7f8f',alpha=.85,ax=ax)
nx.draw_networkx_labels(G,pos,labels={n:n.title() for n in G.nodes()},font_size=8,ax=ax)
# ax.set_title('International country collaboration network')
ax.axis('off'); plt.tight_layout(); plt.savefig('outputs/fig_country_collab.png')
print('-> outputs/fig_country_collab.png')
