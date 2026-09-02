"""Top venues + Bradford core to generate table of sources and show field concentration."""
from common import load
df, c = load()
src = c['source'].str.strip().str.title().value_counts()
print(src.head(15).to_string())
cum = src.cumsum()/src.sum()
print('Bradford core (1/3 of output):', int((cum<=1/3).sum())+1, 'sources of', len(src))
src.head(25).to_csv('outputs/table_top_sources.csv')
