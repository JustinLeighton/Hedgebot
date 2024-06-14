import pandas as pd
import sqlite3
import os

# Create database
con = sqlite3.connect('./modules/fitness/db')
cur = con.cursor()
cur.execute('''
CREATE TABLE IF NOT EXISTS "Workout" (
    "Id"	INTEGER NOT NULL UNIQUE,
    "Hero"	TEXT,
    "Role"	TEXT,
    "URL"	TEXT,
    "<@271088517424218123>" INTEGER,
    "<@295390092304842753>" INTEGER,
    "<@368161555700908033>" INTEGER,
    "<@165300119078436864>" INTEGER,
    "<@717635684436803635>" INTEGER,
    "<@198636588744310784>" INTEGER,
    "<@651554629699633162>" INTEGER,
    PRIMARY KEY("Id" AUTOINCREMENT)
)''')
con.commit()
con.close()

# Read file to load into database
df = pd.read_csv('./modules/hots/backups/OG.csv')

# Create Roster
con = sqlite3.connect('./modules/hots/db')
df.to_sql("Roster", con, if_exists="replace", index=False)
con.close()

# Create pairings
df = pd.read_csv('./modules/hots/backups/Pairings.csv')
con = sqlite3.connect('./modules/hots/db')
df.to_sql("Pairings", con, if_exists="replace", index=False)
con.close()
