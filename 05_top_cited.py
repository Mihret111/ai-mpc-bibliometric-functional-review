"""Most GLOBALLY cited records"""
from common import load
df, c = load()
top = c.nlargest(15,'cites')[['title','year','source','cites','doctype']]
print(top.head(10).to_string(index=False))
top.to_csv('outputs/table_top_cited_GLOBAL.csv', index=False)
