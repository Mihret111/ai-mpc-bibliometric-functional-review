"""annual scientific production and citation maturation
    "citations per document-year" = citations / (2026 - publication year),
      floored at one year. The last two years remain partly censored even after
      normalisation and thus are shaded accordingly.
"""
import pandas as pd, numpy as np, os
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
plt.rcParams.update({'font.size': 8, 'pdf.fonttype': 42})
os.makedirs('outputs', exist_ok=True)
OUT = open('outputs/production_citation_numbers.txt', 'w')
def say(*a):
    s = ' '.join(str(x) for x in a); print(s); OUT.write(s + '\n')

df = pd.read_csv('master_corpus_v2.csv', dtype=str)
for col in ['year', 'cites']: df[col] = pd.to_numeric(df[col], errors='coerce')
df['flag_hard'] = df['flag_hard'].astype(str).str.lower().eq('true')
c = df[~df['flag_hard']].copy()
YEARS = range(2000, 2026)
yr   = c.groupby('year').size().reindex(YEARS, fill_value=0)
core = c[c['doctype'].isin(['article', 'review'])].groupby('year').size().reindex(YEARS, fill_value=0)
tot  = c.groupby('year')['cites'].sum().reindex(YEARS, fill_value=0)
mean = c.groupby('year')['cites'].mean().reindex(YEARS)
c['cpy'] = c['cites'] / (2026 - c['year']).clip(lower=1)
cpy = c.groupby('year')['cpy'].mean().reindex(YEARS)

# ---- numbers ----
x = np.arange(len(yr)); ly = np.log(yr.values.astype(float))
co = np.polyfit(x, ly, 1)
r2 = 1 - ((ly - np.polyval(co, x)) ** 2).sum() / ((ly - ly.mean()) ** 2).sum()
cg = lambda a, b, n: (b / a) ** (1 / n) - 1
say('[production]')
say(f'  2000 {yr[2000]} -> 2025 {yr[2025]} ({yr[2025]/yr[2000]:.0f}-fold), CAGR {100*cg(yr[2000],yr[2025],25):.2f}%')
say(f'  log-linear R2 {r2:.3f}, doubling {np.log(2)/co[0]:.1f} yr')
say(f'  regimes: 2000-2007 {100*cg(yr[2000],yr[2007],7):.2f}% | 2007-2015 {100*cg(yr[2007],yr[2015],8):.2f}% '
    f'| 2015-2020 {100*cg(yr[2015],yr[2020],5):.2f}% | 2020-2025 {100*cg(yr[2020],yr[2025],5):.2f}%')
say(f'  share published after 2015: {100*(c["year"]>2015).mean():.1f}% | after 2020: {100*(c["year"]>2020).mean():.1f}%')
say(f'  2025 output = {yr[2025]/365:.1f} qualifying documents per day')
# data-selected breakpoint
best = None
for cand in range(5, 21):
    rss = 0.0
    for s0, e0 in [(0, cand + 1), (cand, len(x))]:
        rss += ((ly[s0:e0] - np.polyval(np.polyfit(x[s0:e0], ly[s0:e0], 1), x[s0:e0])) ** 2).sum()
    if best is None or rss < best[1]: best = (cand, rss)
bp = best[0]
co1 = np.polyfit(x[:bp+1], ly[:bp+1], 1); co2 = np.polyfit(x[bp:], ly[bp:], 1)
say(f'  data-selected breakpoint {2000+bp}/{2001+bp}; pre {100*(np.exp(co1[0])-1):.1f}%/yr, post {100*(np.exp(co2[0])-1):.1f}%/yr')
say('[citations]')
say(f'  total citations peak {int(tot.max()):,} for publication year {int(tot.idxmax())}')
say(f'  raw mean peak {mean.max():.1f} ({int(mean.idxmax())}) -> {mean[2025]:.1f} (2025)')
say(f'  per-document-year: 2005 {cpy[2005]:.2f} | 2010 {cpy[2010]:.2f} | 2015 {cpy[2015]:.2f} | '
    f'2020 {cpy[2020]:.2f} (peak) | 2025 {cpy[2025]:.2f}')
say(f'  intensity rise 2005->2020: x{cpy[2020]/cpy[2005]:.1f}')

# ---- figure ----
fig, ax = plt.subplots(2, 2, figsize=(6.9, 5.0))
a, b, d, e = ax[0, 0], ax[0, 1], ax[1, 0], ax[1, 1]
a.fill_between(yr.index, yr.values, alpha=.22, color='#2a7f8f')
a.plot(yr.index, yr.values, color='#2a7f8f', lw=1.6, label='Extended corpus')
a.plot(core.index, core.values, color='#7a4fbf', lw=1.6, label='Core (articles + reviews)')
a.set_ylabel('Publications'); a.legend(frameon=False, fontsize=6.6)
a.set_title('(a) annual output', fontsize=8, loc='left')

b.scatter(yr.index, yr.values, s=10, color='#2a7f8f', zorder=3)
b.plot(yr.index[:bp+1], np.exp(np.polyval(co1, x[:bp+1])), color='#D55E00', lw=1.5,
       label=f'{2000}–{2000+bp}: {100*(np.exp(co1[0])-1):.1f}%/yr')
b.plot(yr.index[bp:], np.exp(np.polyval(co2, x[bp:])), color='#0072B2', lw=1.5,
       label=f'{2000+bp}–2025: {100*(np.exp(co2[0])-1):.1f}%/yr')
b.axvline(2000 + bp + .5, color='k', ls=':', lw=.8)
b.set_yscale('log'); b.set_ylabel('Publications (log)'); b.legend(frameon=False, fontsize=6.4)
b.set_title('(b) two exponential regimes', fontsize=8, loc='left')

d.bar(mean.index, mean.values, color='#999999', width=.75)
d.set_ylabel('Mean citations per document'); d.set_xlabel('Publication year')
d.set_title('(c) raw citation counts: censored', fontsize=8, loc='left')
e.bar(cpy.index, cpy.values, color='#009E73', width=.75)
e.set_ylabel('Mean citations per document-year'); e.set_xlabel('Publication year')
e.set_title('(d) age-normalised: intensity rises', fontsize=8, loc='left')
for p in (d, e):
    p.axvspan(2023.5, 2025.5, color='k', alpha=.07)
    p.annotate('partly\ncensored', xy=(2024.5, p.get_ylim()[1] * .82), ha='center', fontsize=5.6, color='0.35')
for p in (a, b, d, e):
    p.spines[['top', 'right']].set_visible(False); p.tick_params(labelsize=7)
plt.tight_layout(); plt.savefig('outputs/fig_production_citations.pdf')
say('\nwrote outputs/fig_production_citations.pdf and production_citation_numbers.txt')
OUT.close()
