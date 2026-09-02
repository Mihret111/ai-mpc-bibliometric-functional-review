"""Fastest-rising keywords 2021-25 vs 2016-20 and generate emerging-fronts table"""
from common import load
import re, pandas as pd
from collections import Counter
exec(open('06_keyword_network.py').read().split('df, c = load()')[0])  # reuse norm/canonmap/kws
df, c = load()
c1,c2 = Counter(),Counter()
for _,r in c[c['auth_kw'].notna()].iterrows():
    if r['year']>=2021: c2.update(kws(r['auth_kw']))
    elif r['year']>=2016: c1.update(kws(r['auth_kw']))
n1,n2 = c['year'].between(2016,2020).sum(), c['year'].between(2021,2025).sum()
rising = sorted([(k,(c2[k]/n2)/((c1[k]+2)/n1)) for k in c2 if c2[k]>=30], key=lambda x:-x[1])[:15]
out = pd.DataFrame(rising, columns=['term','growth_ratio']).round(2)
print(out.to_string(index=False)); out.to_csv('outputs/table_rising_terms.csv', index=False)
