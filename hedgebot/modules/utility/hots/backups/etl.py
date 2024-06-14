#%% Import data

import pandas as pd
import numpy as np
import sqlite3
import os
from bs4 import BeautifulSoup
import requests
from datetime import date

def ETL():

    # Import roster file
    roster = pd.read_csv("./modules/hots/backup/Roster.csv")

    # Create empty lists
    Hero = []
    Duo = []
    Games = []
    Winrate = []

    # Start of loop
    for i in range(len(roster)):

        # Initial variables
        selection = roster["Hero"][i]  # selection = "Anduin"
        url = roster["URL"][i]  # url = "https://www.hotslogs.com/Sitewide/HeroDetails?Hero=Anduin#winRateWithOtherHeroes"

        print(selection)
        print(url)

        # Scrape data
        res = requests.get(url)
        soup = BeautifulSoup(res.text, "html.parser")
        html = str(str(soup.select("td")).encode('utf8'))

        # Loop through a few heroes
        checkvalue = 100.0
        appendflag = False
        loopflag = True
        counter = 0
        while loopflag:

            # Duo hero name
            key = '<a href="/Sitewide/TalentDetails?Hero='
            index = html.find(key)

            if index > 1:

                # Due hero name
                html = html[index + len(key):]
                Duovalue = html[:html.find('"')]

                # Games
                key = '<td>'
                index = html.find(key)
                html = html[index+len(key):]
                Gamesvalue = -1
                try:
                    Gamesvalue = int(html[:html.find('<')])
                except:
                    print(f"Error with game value {html[:html.find('<')]} for {selection} paired with {Duovalue}")

                # Win rate
                key = '<td>'
                index = html.find(key)
                html = html[index+len(key):]
                Winratevalue = -1.0
                try:
                    Winratevalue = float(html[:html.find('<')].strip('%'))
                except:
                    print(f"Error with WR value {html[:html.find('<')].strip('%')} for {selection} paired with {Duovalue}")

                # Check for new data series
                if Winratevalue > checkvalue and not appendflag:
                    appendflag = True
                if not appendflag:
                    checkvalue = Winratevalue

                # Conditional append
                if appendflag:

                    # Clean up hero names
                    Duovalue = Duovalue.replace("Lt.", "")
                    Duovalue = Duovalue.replace("Sgt.", "")
                    Duovalue = Duovalue.replace("The ", "")
                    Duovalue = Duovalue.replace("Lost ", "")
                    Duovalue = Duovalue.replace("Lt.", "")
                    Duovalue = Duovalue.replace("\\xc3\\xba", "u")
                    Duovalue = Duovalue.replace(" ", "")
                    Duovalue = Duovalue.replace("\\", "")
                    Duovalue = Duovalue.replace(".", "")
                    Duovalue = Duovalue.replace("'", "")
                    Duovalue = Duovalue.replace("-", "")

                    # Append values
                    Hero.append(selection)
                    Duo.append(Duovalue)
                    Games.append(Gamesvalue)
                    Winrate.append(Winratevalue)

            else:
                loopflag = False

            if counter > 200:
                loopflag = False

    # Construct dataframe
    df = pd.DataFrame(list(zip(Hero, Duo, Games, Winrate)),
                      columns=["Hero", "Duo", "Games", "Winrate"])
    print(df)

    # Adjusting values
    tmp1 = pd.DataFrame(df["Hero"].unique())
    tmp1.columns = ["Hero"]
    tmp1["key"] = 0
    tmp2 = pd.DataFrame(df["Hero"].unique())
    tmp2.columns = ["Duo"]
    tmp2["key"] = 0
    tmp3 = tmp1.merge(tmp2, how='outer')
    tmp3 = tmp3[tmp3["Hero"] != tmp3["Duo"]]
    df = tmp3.merge(df, how='outer')
    df = df.fillna(0)
    jitter = 5
    df["Winrate"] = (df["Games"] * df["Winrate"] // 100 + jitter) / (df["Games"] + jitter * 2)
    del tmp1, tmp2, tmp3

    # Export
    df.to_csv("./modules/hots/Pairings.csv", index=False)