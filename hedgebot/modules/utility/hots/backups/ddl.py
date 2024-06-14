import pandas as pd
import sqlite3

# Create database
con = sqlite3.connect("./modules/fitness/db")
cur = con.cursor()
cur.execute(
    """
CREATE TABLE IF NOT EXISTS "Workout" (
    "Id"	INTEGER NOT NULL UNIQUE,
    "Item"	TEXT,
    "Date"	TEXT,
    "Day"	TEXT,
    "Person"	TEXT,
    "Value"	FLOAT,
    "Sets"	FLOAT,
    "Reps"	TEXT,
    "Notes"	TEXT,
    "IsActive"	INTEGER,
    PRIMARY KEY("Id" AUTOINCREMENT)
)"""
)
con.commit()
con.close()

# Read file to load into database
df = pd.read_csv("./modules/fitness/load.txt", sep="\t", encoding="utf-16le")

# Connect to SQLite database
con = sqlite3.connect("./modules/fitness/db")
cur = con.cursor()
df.to_sql("Workout", con, if_exists="append", index=False)
con.close()
