"""This is a shared loader that reads the corpus, restores types & applies the screening"""
import pandas as pd, os
def load(path='master_corpus_v1.csv'):
    import os
    if not os.path.exists(path) and os.path.exists('master_corpus_v2.csv'): path='master_corpus_v2.csv'
    df = pd.read_csv(path, dtype=str)
    for c in ['year','cites']: df[c] = pd.to_numeric(df[c], errors='coerce')
    for c in ['flag_hard','flag_rescued','in_both']:
        df[c] = df[c].astype(str).str.lower().eq('true')
    os.makedirs('outputs', exist_ok=True)
    return df, df[~df['flag_hard']].copy()
def body_text(c):
    return (c['title'].fillna('')+' '+c['abstract'].fillna('')+' '+c['auth_kw'].fillna('')).str.lower()
