"""venue analysis: reproduces Figure "Publication venues" and Tables tab_sources / tab_communities"""
import pandas as pd, numpy as np, os, sys
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from venue_lib import key_of, display_of, category
plt.rcParams.update({'font.size': 8, 'pdf.fonttype': 42})
os.makedirs('outputs', exist_ok=True)
LOG = open('outputs/venue_numbers.txt', 'w')
def say(*a):
    s = ' '.join(str(x) for x in a); print(s); LOG.write(s + '\n')

TAIL = 'Long-tail specialist venues'
ERAS = [(2000, 2005), (2006, 2010), (2011, 2015), (2016, 2020), (2021, 2025)]  # same eras as Table tab:growth
ORDER = ['Control & systems', 'AI & computing', 'Process & chemical', 'Manufacturing & materials',
         'Energy & buildings', 'Robotics & vehicles', 'Power electronics & drives',
         'Instrumentation & sensing', 'Mathematics & theory', 'Multidisciplinary journals']
PAL = ['#0072B2', '#E69F00', '#009E73', '#8c6d3a', '#D55E00', '#CC79A7', '#56B4E9', '#7a4fbf', '#8c8c3a', '#666666']

df = pd.read_csv('master_corpus_v2.csv', dtype=str)
df['year'] = pd.to_numeric(df['year'], errors='coerce')
df['flag_hard'] = df['flag_hard'].astype(str).str.lower().eq('true')
c = df[~df['flag_hard']].copy()
raw = c['source'].fillna('').str.strip()

# ---- normalise: one canonical key per venue, one clean display name ----
c['vkey'] = raw.map(key_of)
disp = {}
for k, g in pd.DataFrame({'k': c['vkey'], 'r': raw}).groupby('k'):
    cand = g['r'].value_counts()
    nice = [x for x in cand.index if not x.isupper()]      # prefer a non-ALLCAPS spelling
    disp[k] = display_of(nice[0] if nice else cand.index[0])
c['venue'] = c['vkey'].map(disp)
c['vcat'] = c['venue'].map(category)
say(f'[normalisation] {raw.nunique():,} raw strings -> {c["venue"].nunique():,} venues')

vc = c['venue'].value_counts(); tot = len(c); cs = vc.cumsum()
say('\n[top venues]')
for s, n in vc.head(15).items(): say(f'  {n:4d}  {s[:60]}   [{category(s)}]')

# ---- Bradford zones: three groups of equal record count ----
z1 = int((cs < tot/3).sum()) + 1
z2 = int((cs < 2*tot/3).sum()) + 1 - z1
z3 = len(vc) - z1 - z2
n_mult = z2 / z1
say(f'\n[bradford] zones {z1} : {z2} : {z3}  ->  1 : {n_mult:.1f} : {z3/z1:.1f}')
say(f'  law predicts third zone n^2 = {n_mult**2:.0f}; observed {z3/z1:.1f} '
    f'(periphery {(z3/z1)/(n_mult**2):.1f}x more dispersed than predicted)')
say(f'  core {z1} venues = {100*z1/len(vc):.1f}% of venues, {100*vc.head(z1).sum()/tot:.1f}% of records')
core = c[c['venue'].isin(set(vc.head(z1).index))]
say(f'  core document mix: {core["doctype"].value_counts().to_dict()}')

# ---- community composition; long tail excluded, not relabelled ----
cl = c[c['vcat'] != TAIL]; cov = 100 * len(cl) / tot
say(f'\n[communities] classified coverage {cov:.1f}%; tail = {c[c["vcat"]==TAIL]["venue"].nunique()} venues, '
    f'median size {c[c["vcat"]==TAIL]["venue"].value_counts().median():.0f}')
comp = pd.DataFrame({f'{a}–{b}': cl[cl['year'].between(a, b)]['vcat'].value_counts(normalize=True) * 100
                     for a, b in ERAS}).fillna(0)
comp = comp.reindex([k for k in ORDER if k in comp.index]).round(1)
say(comp.to_string())

# ---- figure ----
fig, (p1, p2) = plt.subplots(1, 2, figsize=(6.9, 3.4))
p1.plot(np.arange(1, len(vc) + 1), 100 * (cs / tot).values, color='#0072B2', lw=1.7)
for z, lab in [(z1, f'zone 1 ({z1})'), (z1 + z2, f'zone 2 ({z2})')]:
    p1.axvline(z, color='k', ls=':', lw=.8)
    p1.annotate(lab, xy=(z, 5), fontsize=5.8, rotation=90, ha='right', color='0.3')
p1.set_xscale('log'); p1.set_xlabel('Venue rank (log scale)'); p1.set_ylabel('Cumulative % of records')
p1.set_title(f'(a) Bradford zones  {z1} : {z2} : {z3}', fontsize=8, loc='left')
p1.spines[['top', 'right']].set_visible(False)
bottom = np.zeros(len(ERAS))
for k in comp.index:
    p2.bar(range(len(ERAS)), comp.loc[k].values, bottom=bottom, color=PAL[ORDER.index(k)], label=k, width=.62)
    bottom += comp.loc[k].values
p2.set_xticks(range(len(ERAS))); p2.set_xticklabels(comp.columns, fontsize=6.2, rotation=20)
p2.set_ylabel('% of classified output'); p2.set_ylim(0, 100)
p2.legend(frameon=False, fontsize=5.2, loc='upper center', bbox_to_anchor=(.5, -.22), ncol=2)
p2.set_title('(b) publishing communities', fontsize=8, loc='left')
p2.spines[['top', 'right']].set_visible(False)
plt.tight_layout(); plt.savefig('outputs/fig_venues.pdf', bbox_inches='tight')

# ---- tables ----
esc = lambda s: str(s).replace('&', '\\&')
rows = '\n'.join(f'{esc(s)[:52]} & {esc(category(s))[:24]} & {n} & {100*n/tot:.1f} \\\\' for s, n in vc.head(15).items())
open('outputs/tab_sources.tex', 'w').write(
 '\\begin{table}[t]\\centering\\caption{Most productive venues after source normalisation (year-stamped, case, and '
 f'publisher-suffix variants merged). A Bradford core of {z1} venues carries one third of output.'
 '}\\label{tab:sources}\n{\\footnotesize\\begin{tabular}{p{5.9cm}p{3.0cm}rr}\\toprule\n'
 'Venue & Community & Records & \\% \\\\ \\midrule\n' + rows + '\n\\bottomrule\\end{tabular}}\\end{table}\n')
rows2 = '\n'.join(f'{esc(k)} & ' + ' & '.join(f'{comp.loc[k,cc]:.1f}' for cc in comp.columns) + ' \\\\' for k in comp.index)
open('outputs/tab_communities.tex', 'w').write(
 '\\begin{table}[t]\\centering\\caption{Share of classified output by publishing community (\\%), using the same '
 f'five-year eras as Table~\\\\ref{{tab:growth}}. Shares cover the {cov:.1f}\\% of records in classified venues; the '
 'remainder lies in a long tail of venues with a median of one record each.'
 '}\\label{tab:communities}\n{\\footnotesize\\begin{tabular}{lrrrrr}\\toprule\nCommunity & '
 + ' & '.join(comp.columns) + ' \\\\ \\midrule\n' + rows2 + '\n\\bottomrule\\end{tabular}}\\end{table}\n')
say('\nwrote outputs/fig_venues.pdf, tab_sources.tex, tab_communities.tex, venue_numbers.txt')
LOG.close()
