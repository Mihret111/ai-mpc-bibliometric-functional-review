"""co-citation of cited references = the intellectual base"""
from common import load
import pandas as pd, re, itertools
from collections import Counter
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
import networkx as nx
df, c = load('master_corpus_v2.csv')
sub = c[c['wos_cr'].notna()].copy()
def refkey(s):
    p=[x.strip() for x in str(s).split(',')]
    if len(p)<3: return None
    a=re.sub(r'[^a-z ]','',p[0].lower()).strip(); y=p[1].strip()
    return f'{a}, {y}, {p[2].strip().lower()[:22]}' if a and y.isdigit() else None
sub['rset']=sub['wos_cr'].map(lambda s:{k for k in (refkey(x) for x in str(s).split(';')) if k})
def build(mask,label):
    d=sub[mask]['rset']; cnt=Counter(); [cnt.update(x) for x in d]
    nodes={k for k,v in cnt.items() if v>=40*mask.mean()}
    co=Counter()
    for x in d:
        for a,b in itertools.combinations(sorted(x & nodes),2): co[(a,b)]+=1
    G=nx.Graph(); G.add_weighted_edges_from((a,b,w) for (a,b),w in co.items() if w>=10*mask.mean())
    comms=[x for x in nx.community.greedy_modularity_communities(G,weight='weight') if len(x)>=8]
    print(f'{label}: docs {mask.sum():,} | nodes {G.number_of_nodes()} | clusters {len(comms)}')
    return cnt,G,comms
mask_all=pd.Series(True,index=sub.index)
cnt,G,comms=build(mask_all,'EXTENDED')
cnt_core,_,_=build(sub['doctype'].isin(['article','review']),'CORE')
t1=[k for k,_ in cnt.most_common(20)]; t2=[k for k,_ in cnt_core.most_common(20)]
print(f'top-20 overlap: {len(set(t1)&set(t2))}/20')
print('top-10 co-cited:'); [print(f'  {v:5d}  {k}') for k,v in cnt.most_common(10)]
pos=nx.spring_layout(G,k=.45,seed=2,weight='weight'); cm={k:i for i,x in enumerate(comms) for k in x}
fig,ax=plt.subplots(figsize=(11,8.5),dpi=150)
nx.draw_networkx_edges(G,pos,alpha=.08,ax=ax)
nx.draw_networkx_nodes(G,pos,node_size=[cnt[n]*.9 for n in G.nodes()],node_color=plt.cm.tab10([cm.get(n,9)%10 for n in G.nodes()]),alpha=.85,ax=ax)
lab={n:n.split(',')[0].title()+' '+n.split(',')[1] for n in sorted(G.nodes(),key=lambda k:-cnt[k])[:35]}
nx.draw_networkx_labels(G,pos,labels=lab,font_size=6.5,ax=ax)
# ax.set_title('Co-citation network of cited references')
ax.axis('off'); plt.tight_layout(); plt.savefig('outputs/fig_cocitation_network.png')
print('-> outputs/fig_cocitation_network.png')
