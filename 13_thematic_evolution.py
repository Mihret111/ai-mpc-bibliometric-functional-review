"""Keyword share per era ---- themes being born and fading"""
from common import load
import pandas as pd, re
from collections import Counter
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
FAM={'neural network':'neural network|ann|artificial neural network|neural net|mlp',
 'generalized predictive control':'generalized predictive control|gpc',
 'genetic algorithm':'genetic algorithm|ga','particle swarm optimization':'particle swarm optimization|pso',
 'reinforcement learning':'reinforcement learning|rl','deep reinforcement learning':'deep reinforcement learning|drl',
 'long short term memory':'long short term memory|lstm','support vector machine':'support vector machine|svm|svr',
 'gaussian process':'gaussian process|gpr','nonlinear model predictive control':'nonlinear model predictive control|nmpc',
 'multi objective optimization':'multi objective optimization|multiobjective optimization'}
canonmap={v:c for c,p in FAM.items() for v in p.split('|')}
def norm(k):
    k=re.sub(r'\(.*?\)','',k).replace('-',' '); k=re.sub(r'\s+',' ',k).strip()
    k=re.sub(r'isation\b','ization',k); k=re.sub(r'ised\b','ized',k)
    return k[:-1] if k.endswith('s') and not k.endswith('ss') and len(k)>4 else k
def kws(s): return {canonmap.get(norm(x.strip().lower()),norm(x.strip().lower())) for x in str(s).split(';') if x.strip()}
DROP={'model predictive control','predictive control','optimization','optimal control','control'}
df,c=load('master_corpus_v2.csv.gz')
share={}
for a,b in [(2000,2005),(2006,2010),(2011,2015),(2016,2020),(2021,2025)]:
    sub=c[c['year'].between(a,b)&c['auth_kw'].notna()]
    cn=Counter(); [cn.update(kws(s)) for s in sub['auth_kw']]
    share[f'{a}-{b}']={k:100*v/len(sub) for k,v in cn.items() if k not in DROP}
S=pd.DataFrame(share).fillna(0)
T=S.loc[S.max(axis=1).nlargest(24).index].copy()
T['pk']=T.values.argmax(axis=1); T=T.sort_values('pk').drop(columns='pk')
fig,ax=plt.subplots(figsize=(9.5,7),dpi=150)
im=ax.imshow(T.values,cmap='YlGnBu',aspect='auto')
ax.set_xticks(range(5)); ax.set_xticklabels(T.columns,fontsize=8)
ax.set_yticks(range(len(T))); ax.set_yticklabels(T.index,fontsize=7.5)
# ax.set_title('Thematic evolution heatmap')
plt.colorbar(im,label='% of era records'); plt.tight_layout()
plt.savefig('outputs/fig_thematic_evolution.png'); T.round(2).to_csv('outputs/table_thematic_evolution.csv')
born=[k for k in S.index if S.loc[k,'2000-2005']<0.3 and S.loc[k,'2021-2025']>=1.2]
faded=[k for k in S.index if S.loc[k,'2000-2005']>=1.5 and S.loc[k,'2021-2025']<S.loc[k,'2000-2005']/3]
print('BORN:',sorted(born,key=lambda k:-S.loc[k,'2021-2025'])[:8])
print('FADED:',sorted(faded,key=lambda k:-S.loc[k,'2000-2005'])[:8])
