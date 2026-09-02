"""Annual Publications by Year"""
from common import load
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
df, c = load()
yr = c.groupby('year').size()
core = c[c['doctype'].isin(['article','review'])].groupby('year').size()
print(f"2000: {yr[2000]} -> 2025: {yr[2025]} | CAGR {100*((yr[2025]/yr[2000])**(1/25)-1):.1f}%/yr")
fig, ax = plt.subplots(figsize=(9,4.5), dpi=150, )
ax.fill_between(yr.index, yr.values, alpha=.25, color='#2a7f8f')
ax.plot(yr.index, yr.values, color='#2a7f8f', lw=2, label=f'Article + Review + conference proceedings (n={len(c):,})')
ax.plot(core.index, core.values, color='#7a4fbf', lw=2, label=f'Article + Review  (n={int(core.sum()):,})')
# ax.set_title('Annual Publications by Year')
ax.set_xlabel('Year'); ax.set_ylabel('Publications'); ax.legend(frameon=False)
ax.spines[['top','right']].set_visible(False); plt.tight_layout()
plt.savefig('outputs/fig_annual_production.png'); print('-> outputs/fig_annual_production.png')
