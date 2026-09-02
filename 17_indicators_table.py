""" produces Table "Main bibliometric characteristics" computed from the corpus

DEFINITIONS 
  Scopus-indexed  = records retained from Scopus  = dual-indexed + Scopus-only
  WoS-indexed     = dual-indexed + WoS-only
  Sources        = venues after normalisation (venue_lib)(!= raw strings)
  Cited refs     = reference strings in each database's native export format,
                   counted with a format-specific rule (nrefs docstring)
                   Co-citation and coupling use WoS-format strings only, so the
                   merged figure equals the WoS figure by construction
  Authors        = distinct author-name strings. This is a lower-bound estimate; no identifier disambiguation is applied.
"""
import pandas as pd, numpy as np, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from venue_lib import key_of, display_of
os.makedirs('outputs', exist_ok=True)

df = pd.read_csv('master_corpus_v2.csv', dtype=str)
for k in ['year', 'cites']: df[k] = pd.to_numeric(df[k], errors='coerce')
for k in ['flag_hard', 'in_both']: df[k] = df[k].astype(str).str.lower().eq('true')
c = df[~df['flag_hard']].copy()

SUB = {'Scopus': c[c['db'] == 'scopus'],
       'Web of Science': c[c['in_both'] | (c['db'] == 'wos')],
       'Merged': c}

def venues(x):
    raw = x['source'].fillna('').str.strip(); k = raw.map(key_of)
    d = {}
    for kk, g in pd.DataFrame({'k': k, 'r': raw}).groupby('k'):
        cand = g['r'].value_counts(); nice = [y for y in cand.index if not y.isupper()]
        d[kk] = display_of(nice[0] if nice else cand.index[0])
    return k.map(d).nunique()

def nrefs(x, col):
    """Counting rule differs by database format.
    WoS CR: one reference per ';'-separated entry -> split on ';'.
    Scopus References: ';' also separates AUTHORS inside a reference, so a
    ';'-split triple-counts (104 vs 31 refs/doc). Each Scopus reference instead
    ends in a '(year)' field, so year anchors are the reliable unit."""
    import re as _re
    s = x[col].dropna()
    if not len(s): return 0
    if col == 'wos_cr':
        return int(s.map(lambda t: len([y for y in str(t).split(';') if y.strip()])).sum())
    return int(s.map(lambda t: len(_re.findall(r'\((?:19|20)\d\d\)', str(t)))).sum())

def authors(x):
    a = set()
    for s in x['authors'].dropna():
        a |= {t.strip().lower() for t in str(s).split(';') if t.strip()}
    return len(a)

rows = {}
for lab, x in SUB.items():
    yr = x.groupby('year').size()
    g = (yr.get(2025, 0) / max(yr.get(2000, 1), 1)) ** (1/25) - 1
    apd = x['authors'].dropna().map(lambda s: len([t for t in str(s).split(';') if t.strip()]))
    rows[lab] = {
        'Timespan': '2000--2025',
        'Documents': f'{len(x):,}',
        'Sources (normalised venues)': f'{venues(x):,}',
        'Annual growth rate (\\%)': f'{100*g:.2f}',
        'Document average age (years)': f'{(2026 - x["year"]).mean():.2f}',
        'Average citations per document': f'{x["cites"].mean():.2f}',
        'Average citations per document-year': f'{(x["cites"]/(2026-x["year"]).clip(lower=1)).mean():.3f}',
        'Cited references parsed$^{b}$': f'{nrefs(x, "refs" if lab=="Scopus" else "wos_cr"):,}',
        'Distinct author names$^{c}$': f'{authors(x):,}',
        'Authors per document': f'{apd.mean():.2f}',
        'Single-authored documents': f'{int((apd==1).sum()):,}',
        'International co-authorship (\\%)': '--',
        'Articles': f'{int((x["doctype"]=="article").sum()):,}',
        'Conference papers': f'{int((x["doctype"]=="conference").sum()):,}',
        'Reviews': f'{int((x["doctype"]=="review").sum()):,}',
    }
# international co-authorship: merged only (affiliation parsing)
import re
FIXC = {'peoples r china':'china','united states':'usa','u.s.a':'usa','england':'united kingdom',
        'scotland':'united kingdom','wales':'united kingdom','north ireland':'united kingdom',
        'republic of korea':'south korea','korea':'south korea','russian federation':'russia',
        'viet nam':'vietnam','turkiye':'turkey'}
def ctry(s):
    out = set()
    for a in str(s).split(';'):
        t = re.sub(r'\d+', '', a.split(',')[-1].strip().lower().rstrip('.')).strip()
        if 2 < len(t) < 30: out.add(FIXC.get(t, t))
    return out
for lab, x in SUB.items():
    rows[lab]['International co-authorship (\\%)'] = f'{100*(x["aff"].map(ctry).map(len)>=2).mean():.1f}'

ORDER = list(rows['Merged'].keys())
body = '\n'.join(
    f'{k} & {rows["Scopus"][k]} & {rows["Web of Science"][k]} & \\textbf{{{rows["Merged"][k]}}} \\\\'
    for k in ORDER)
tex = (
'\\begin{table}[t]\\centering\n'
'\\caption{Main bibliometric characteristics of the screened corpus.}\n'
'\\label{tab:indicators}\n{\\footnotesize\\begin{tabular}{lrrr}\\toprule\n'
'Indicator & Scopus$^{a}$ & Web of Science$^{a}$ & \\textbf{Merged} \\\\ \\midrule\n'
+ body + '\n\\bottomrule\\end{tabular}\\\\[2pt]\n'
'\\begin{minipage}{0.94\\linewidth}\\scriptsize\n'
'$^{a}$ The 8{,}561 records indexed in both databases are counted in both single-database '
'columns, which therefore do not sum to the merged column; this double counting is why every '
'other descriptive statistic in this paper is computed on the merged corpus.\\\\\n'
'$^{b}$ Reference strings in each database\'s native export format. Co-citation and '
'bibliographic coupling use Web of Science strings only, whose fielded format supports uniform '
'parsing, so the merged figure equals the Web of Science figure by construction.\\\\\n'
'$^{c}$ Distinct author-name strings after case folding; no identifier disambiguation is '
'applied, so this is a lower bound on the true author count.\n'
'\\end{minipage}}\\end{table}\n')
open('outputs/tab_indicators.tex', 'w').write(tex)
print(pd.DataFrame(rows).loc[ORDER].to_string())
print('\n-> outputs/tab_indicators.tex')
