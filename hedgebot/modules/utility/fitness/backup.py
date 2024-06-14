import pandas as pd
import sqlite3
from datetime import date

# Connect to SQLite database
con = sqlite3.connect("./modules/fitness/db")
cur = con.cursor()
db = pd.read_sql_query("SELECT * FROM Workout WHERE IsActive = 1", con)
con.close()

# Output backup
db.to_csv(f"./modules/fitness/backups/{str(date.today())}_backup.txt", sep="\t", encoding="utf-16le")
