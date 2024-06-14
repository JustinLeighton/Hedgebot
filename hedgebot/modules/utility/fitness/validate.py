import pandas as pd
import os

df = pd.read_csv('./modules/fitness/load.txt', sep='\t', encoding = 'utf-16le')

tmp = pd.merge(df[df['IsActive'] == 0],
               df[df['IsActive'] == 1],
               on=['Item', 'Day', 'Person'],
               how='left')
tmp = tmp[tmp['IsActive_y'].isna()]
print('Missing:', tmp.shape[0])

tmp = df[df['IsActive'] == 1].groupby(['Item', 'Day', 'Person']).count()
print('dupes:', tmp[tmp['IsActive'] > 1].shape[0])
