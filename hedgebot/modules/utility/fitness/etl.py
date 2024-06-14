#%% Import data

import pandas as pd
import numpy as np
import sqlite3
import os
from datetime import date

# Read from sheets
with open('sheet.txt') as f:
    sheet_id = f.read()
df = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv")


# Define preprocessing function
def preprocessing(df):
    tmp = df.copy()
    for field in ['Item', 'Person', 'Notes', 'Day', 'Sets', 'Reps']:
        tmp[field] = tmp[field].astype(str).str.split('.', expand=True)[0]
        tmp[field] = tmp[field].astype('object')
        tmp[field] = tmp[field].fillna(value=' ')
    tmp = tmp.replace({np.nan: None, 'nan': None, 'NaN': None, 'None': None})
    tmp['Value'] = tmp['Value'].astype('float64')
    return tmp


# Connect to SQLite database
con = sqlite3.connect("./modules/fitness/db")
cur = con.cursor()
db = pd.read_sql_query('SELECT * FROM Workout WHERE IsActive = 1', con)
db = db.drop(['IsActive', 'Date'], axis=1)
db = preprocessing(db)
db['Id'] = db['Id'].astype('int')
con.close()


#%% Transform

# Fill missing days
df['Day'] = df['Day'].fillna(method='ffill')

# Select fields
df = df[['Day', 'Item', 'Sets', 'Reps', 'Kenn', 'Justin', 'Notes']]

# Pivot on name
df = pd.concat([df[['Day', 'Item', 'Sets', 'Reps', 'Notes', 'Kenn']].rename({'Kenn': 'Value'}, axis=1),
                df[['Day', 'Item', 'Sets', 'Reps', 'Notes', 'Justin']].rename({'Justin': 'Value'}, axis=1)],
               keys=['Kenn', 'Justin']).reset_index()
df = df.rename({'level_0': 'Person'}, axis=1).drop('level_1', axis=1)

# Convert data types
df = preprocessing(df)


#%% Compare sheets to db

# Join
changes = pd.merge(df, db, on=['Item', 'Day', 'Person'], how='outer')

# Check for changes
changes = changes[~(changes['Sets_x'].eq(changes['Sets_y'])) |
                  ~(changes['Reps_x'].eq(changes['Reps_y'])) |
                  ~(changes['Notes_x'].eq(changes['Notes_y'])) |
                  ~(changes['Value_x'].eq(changes['Value_y']))]
changes = changes[~((changes['Value_x'].isna()) & (changes['Value_y'].isna()))]


#%% Output

# Flip IsActive to zero
# cur = con.cursor()
# cur.execute('UPDATE Workout SET IsActive = 0 WHERE Id IN (' + ','.join(changes['Id'].astype(str).tolist()) + ')')
# cur.close()
print('Inactive:', ','.join(changes['Id'].astype(str).tolist()))

# Insert removed as null records
tmp = changes[changes['Value_x'].isna()].copy()
for field in ['Sets', 'Reps', 'Notes', 'Value']:
    tmp[field] = None
tmp['Value'] = tmp['Value'].astype('float64')
tmp['Date'] = str(date.today().strftime("%Y-%m-%d"))
tmp['IsActive'] = 1
tmp = tmp[['Item', 'Date', 'Day', 'Person', 'Value', 'Sets', 'Reps', 'Notes', 'IsActive']]
# tmp.to_sql("Workout", con, if_exists="append", index=False)
print('Case 1:', tmp.shape)

# Insert changed records
tmp = changes[~changes['Value_x'].isna()].copy()
tmp = tmp.rename({'Sets_x': 'Sets', 'Reps_x': 'Reps', 'Notes_x': 'Notes', 'Value_x': 'Value'}, axis=1)
tmp['Date'] = str(date.today().strftime("%Y-%m-%d"))
tmp['IsActive'] = 1
tmp = tmp[['Item', 'Date', 'Day', 'Person', 'Value', 'Sets', 'Reps', 'Notes', 'IsActive']]
# changes.to_sql("Workout", con, if_exists="append", index=False)
print('Case 2:', tmp.shape)
print('Total: ', changes.shape)
