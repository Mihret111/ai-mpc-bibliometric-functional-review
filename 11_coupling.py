"""Bibliographic coupling of 2021-2025 core documents = research fronts"""
from common import load
import pandas as pd, re, itertools
from collections import Counter, defaultdict
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
import networkx as nx
df, c = load('master_corpus_v2.csv')
sub = c[c['wos_cr'].notna() & c['year'].between(2021,2025) & c['doctype'].isin(['article','review'])].reset_index(drop=True)
def refkey(s):
    p=[x.strip() for x in str(s).split(',')]
    if len(p)<3: return None
    a=re.sub(r'[^a-z ]','',p[0].lower()).strip(); y=p[1].strip()
    return f'{a},{y},{p[2].strip().lower()[:20]}' if a and y.isdigit() else None
sub['rset']=sub['wos_cr'].map(lambda s:{k for k in (refkey(x) for x in str(s).split(';')) if k})
sub=sub[sub['rset'].map(len)>=10].reset_index(drop=True)
inv=defaultdict(list)
for i,rs in enumerate(sub['rset']):
    for r in rs: inv[r].append(i)
pair=Counter()
for r,docs in inv.items():
    if 2<=len(docs)<=150:
        for a,b in itertools.combinations(docs,2): pair[(a,b)]+=1
G=nx.Graph(); G.add_weighted_edges_from((a,b,w) for (a,b),w in pair.items() if w>=8)
comms=[x for x in nx.community.greedy_modularity_communities(G,weight='weight') if len(x)>=40]
print(f'docs {len(sub)} | network {G.number_of_nodes()} nodes | fronts {len(comms)}')
stop=set('a the of and for with using based on in to model predictive control mpc via an by'.split())
for i,x in enumerate(comms[:8]):
    w=Counter()
    for j in x: w.update(t for t in re.findall(r'[a-z]+',str(sub.loc[j,"title"]).lower()) if t not in stop and len(t)>3)
    print(f'  F{i+1} (n={len(x)}):', ', '.join(k for k,_ in w.most_common(5)))
pos=nx.spring_layout(G,k=.25,seed=6,weight='weight'); cm={j:i for i,x in enumerate(comms) for j in x}
fig,ax=plt.subplots(figsize=(10,8),dpi=150)
nx.draw_networkx_edges(G,pos,alpha=.04,ax=ax)
nx.draw_networkx_nodes(G,pos,node_size=14,node_color=plt.cm.tab10([cm.get(n,9)%10 for n in G.nodes()]),alpha=.8,ax=ax)
# ax.set_title('Bibliographic coupling network of research fronts')
ax.axis('off'); plt.tight_layout(); plt.savefig('outputs/fig_coupling_fronts.png')
print('-> outputs/fig_coupling_fronts.png')
