"""Thesaurus + keyword co-occurrence network 
Additionally generates VOSviewer input files """
from common import load
import pandas as pd, re, itertools, networkx as nx
from collections import Counter
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
FAM = {
 'neural network':'neural network|ann|artificial neural network|neural net|nn model|feedforward neural network|multilayer perceptron|mlp',
 'model predictive control':'model predictive control|mpc|model based predictive control|predictive control strategy',
 'generalized predictive control':'generalized predictive control|gpc',
 'genetic algorithm':'genetic algorithm|ga',
 'particle swarm optimization':'particle swarm optimization|pso|particle swarm',
 'reinforcement learning':'reinforcement learning|rl',
 'deep reinforcement learning':'deep reinforcement learning|drl',
 'long short term memory':'long short term memory|lstm|lstm network',
 'support vector machine':'support vector machine|svm|support vector regression|svr|least square support vector machine|ls svm',
 'gaussian process':'gaussian process|gaussian process regression|gpr',
 'fuzzy logic':'fuzzy logic|fuzzy logic control',
 'takagi sugeno fuzzy model':'takagi sugeno fuzzy model|t s fuzzy model|ts fuzzy|takagi sugeno',
 'radial basis function network':'radial basis function network|rbf network|rbf neural network|rbfnn',
 'nonlinear model predictive control':'nonlinear model predictive control|nmpc|nonlinear mpc',
 'adaptive neuro fuzzy inference system':'adaptive neuro fuzzy inference system|anfi',
 'permanent magnet synchronous motor':'permanent magnet synchronous motor|pmsm|ipmsm'}
DROP = {'model predictive control','predictive control','optimization','optimal control','control'}
def norm(k):
    k = re.sub(r'\(.*?\)','',k).replace('-',' ')
    k = re.sub(r'\s+',' ',k).strip()
    k = re.sub(r'isation\b','ization',k); k = re.sub(r'ised\b','ized',k); k = k.replace('modelling','modeling')
    return k[:-1] if k.endswith('s') and not k.endswith('ss') and len(k)>4 else k
canonmap = {v:c for c,p in FAM.items() for v in p.split('|')}
def kws(s): return {canonmap.get(norm(x.strip().lower()),norm(x.strip().lower())) for x in str(s).split(';') if x.strip()}
df, c = load()
docs = c[c['auth_kw'].notna()]['auth_kw'].map(kws)
occ = Counter(); [occ.update(d) for d in docs]
keep = {k for k,v in occ.items() if v>=20} - DROP
print('terms >=20 occurrences (after drop-list):', len(keep))
co = Counter()
for d in docs:
    for a,b in itertools.combinations(sorted(d & keep),2): co[(a,b)]+=1
G = nx.Graph(); G.add_weighted_edges_from((a,b,w) for (a,b),w in co.items() if w>=3)
comms = nx.community.greedy_modularity_communities(G, weight='weight')
print('nodes', G.number_of_nodes(), '| edges', G.number_of_edges(), '| communities', len([x for x in comms if len(x)>=10]))
top60 = sorted(keep, key=lambda k:-occ[k])[:60]; H = G.subgraph(top60)
cmap = {k:i for i,cm in enumerate(comms) for k in cm}
pos = nx.spring_layout(H, k=.6, seed=4, weight='weight')
fig, ax = plt.subplots(figsize=(11,8), dpi=150)
nx.draw_networkx_edges(H,pos,alpha=.12,ax=ax)
nx.draw_networkx_nodes(H,pos,node_size=[occ[n]*1.5 for n in H.nodes()],
    node_color=plt.cm.tab10([cmap.get(n,9)%10 for n in H.nodes()]),alpha=.85,ax=ax)
nx.draw_networkx_labels(H,pos,font_size=7,ax=ax)
# ax.set_title('Keyword co-occurrence network')
ax.axis('off')
plt.tight_layout(); plt.savefig('outputs/fig_keyword_network_preview.png')
# VOSviewer inputs
sub = c.rename(columns={'title':'Title','year':'Year','source':'Source title','auth_kw':'Author Keywords',
 'idx_kw':'Index Keywords','doi':'DOI','cites':'Cited by','authors':'Authors','doctype_raw':'Document Type','abstract':'Abstract'})
sub[['Authors','Title','Year','Source title','Author Keywords','Index Keywords','Cited by','DOI','Document Type','Abstract']].to_csv('outputs/vosviewer_corpus.csv', index=False)
with open('outputs/thesaurus_keywords.txt','w') as f:
    f.write('label\treplace by\n')
    seen=set()
    for _,r in c[c['auth_kw'].notna()].iterrows():
        for raw in str(r['auth_kw']).split(';'):
            raw=raw.strip().lower()
            if not raw or raw in seen: continue
            seen.add(raw); tgt=canonmap.get(norm(raw),norm(raw))
            if raw!=tgt and occ.get(tgt,0)>=15: f.write(f'{raw}\t{tgt}\n')
print('-> outputs/: network figure + vosviewer_corpus.csv + thesaurus_keywords.txt')
