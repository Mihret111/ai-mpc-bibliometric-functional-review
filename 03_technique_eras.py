"""Share of records per AI family per year"""

from common import load, body_text
import pandas as pd, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
FAM = {
 'Neural networks / DL': r'neural network|deep learning|lstm|long short.term memory|convolutional|autoencoder|auto.encoder|radial basis function|extreme learning|echo state|gated recurrent|recurrent neural',
 'Reinforcement learning': r'reinforcement learning|q.learning|actor.critic|policy gradient|adaptive dynamic programming|approximate dynamic programming|deep deterministic|soft actor',
 'Fuzzy systems': r'fuzzy|anfis|takagi.sugeno',
 'Evolutionary / swarm': r'genetic algorithm|genetic programming|evolutionary|differential evolution|particle swarm|ant colony|bee colony|swarm intelligence|metaheuristic|simulated annealing|grey wolf|gray wolf|whale optimi|cuckoo|firefly|bat algorithm|harmony search',
 'Probabilistic / kernel': r'gaussian process|kriging|support vector|bayesian optimi|bayesian linear',
 'Tree ensembles': r'random forest|gradient boost|xgboost'}
df, c = load(); body = body_text(c)
for f,p in FAM.items(): c[f] = body.str.contains(p, regex=True)
eras = [(2000,2005),(2006,2010),(2011,2015),(2016,2020),(2021,2025)]
tab = pd.DataFrame({f:[100*c[c['year'].between(a,b)][f].mean() for a,b in eras] for f in FAM},
                   index=[f'{a}-{b}' for a,b in eras]).round(1)
print(tab.to_string()); tab.to_csv('outputs/table_technique_eras.csv')
yearly = pd.DataFrame({f: c.groupby('year')[f].mean()*100 for f in FAM})
ax = yearly.rolling(3,center=True,min_periods=1).mean().plot(figsize=(9.5,5), lw=2)
ax.set_ylabel('% of records'); ax.legend(frameon=False, fontsize=8)
ax.spines[['top','right']].set_visible(False)
# ax.set_title('Share of records per AI family per year')
plt.tight_layout(); plt.savefig('outputs/fig_technique_eras.png', dpi=150)
print('-> outputs/fig_technique_eras.png')
