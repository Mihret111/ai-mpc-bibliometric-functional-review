"""Sanity-check the dataset"""
from common import load
df, c = load()
print('total records:', len(df))
print('screened corpus:', len(c), '| excluded:', df['flag_hard'].sum())
print('doc types:', c['doctype'].value_counts().to_dict())
print('core (articles+reviews):', c['doctype'].isin(['article','review']).sum())
print('year range:', int(c['year'].min()), '-', int(c['year'].max()))