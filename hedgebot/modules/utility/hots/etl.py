import hashlib
import gc

import pandas as pd

from db import SQLiteManager


db = SQLiteManager("hedgebot/modules/utility/hots/db.sqlite3")


def get_hash(input_string: str, length: int = 8):
    hash_object = hashlib.sha256()
    hash_object.update(input_string.encode("utf-8"))
    hash_str = hash_object.hexdigest()
    short_hash = hash_str[:length]
    hash_int = int(short_hash, 16)
    return hash_int


def run_hots_etl():

    # https://heroesofthestorm.fandom.com/wiki/Heroes_of_the_Storm_Wiki/Heroes
    df_roles = pd.read_csv("hedgebot/modules/utility/hots/data/roles.csv", sep="\t", header=None)
    db.drop_table(table_name="ROLES")
    db.table(table_name="ROLES", columns={"ROLE": "TEXT", "STUB": "TEXT"})
    for _, row in df_roles.iterrows():
        id = get_hash(row[0])
        db.execute_query(
            f"""
            INSERT INTO ROLES (ID, ROLE, STUB)
                VALUES ({id}, '{row[0]}', '{row[1]}')
        """
        )
    df_roles = db.execute_query("SELECT * FROM ROLES")
    print("\n~~~\ndf_roles:\n", df_roles)

    df_heroes = None
    if df_roles is not None:
        # https://www.heroesprofile.com/Global/Hero?timeframe_type=major&timeframe=2.55&game_type=qm
        df_heroes = pd.read_csv("hedgebot/modules/utility/hots/data/heroes.csv", sep="\t", header=None)
        db.drop_table(table_name="HEROES")
        db.table(table_name="HEROES", columns={"HERO": "TEXT", "ROLE_ID": "INT", "GAMES": "INT", "WINRATE": "REAL"})
        df_heroes.columns = ["HERO", "ROLE", "GAMES", "WINRATE"]
        df = pd.merge(df_heroes, df_roles, on="ROLE")
        df = df[["HERO", "ID", "GAMES", "WINRATE"]]
        for _, row in df.iterrows():
            id = get_hash(row[0])
            db.execute_query(
                f"""
                INSERT INTO HEROES (ID, HERO, ROLE_ID, GAMES, WINRATE)
                    VALUES ({id}, '{row[0].replace("'", "")}', {row[1]}, {row[2]}, {row[3]})
            """
            )
        df_heroes = db.execute_query("SELECT * FROM HEROES")
        print("\n~~~\ndf_heroes:\n", df_heroes)

    if df_heroes is not None and df_roles is not None:
        # https://www.heroesprofile.com/Global/Compositions?timeframe_type=major&timeframe=2.55&game_type=qm&hero=Abathur
        df = pd.read_csv("hedgebot/modules/utility/hots/data/composition.csv", sep="\t")
        df_composition = df[df["Table"] == 1][["CompID", "Hero", "Win Rate %", "Games Played"]]
        df_composition_role = df[df["Table"] == 2][["CompID", "Role"]]
        del df
        gc.collect()

        # Composition
        df_composition = pd.merge(df_composition, df_heroes, left_on="Hero", right_on="HERO")
        df_composition = df_composition[["CompID", "ID", "Games Played", "Win Rate %"]]
        db.drop_table(table_name="COMPOSITION")
        db.table(
            table_name="COMPOSITION",
            columns={"HERO_ID": "INT", "GAMES": "INT", "SCORE": "REAL"},
        )
        for _, row in df_composition.iterrows():

            db.execute_query(
                f"""
                INSERT INTO COMPOSITION (ID, HERO_ID, GAMES, SCORE)
                    VALUES ({row[0]}, {row[1]}, {row[2]}, {row[3]})
            """
            )
        df_composition = db.execute_query("SELECT * FROM COMPOSITION")
        print("\n~~~\ndf_composition:\n", df_composition)

        # Composition Role
        df_composition_role = pd.merge(df_composition_role, df_roles, left_on="Role", right_on="ROLE")
        df_composition_role = df_composition_role[["CompID", "ID"]]
        df_composition_role = df_composition_role.groupby(["CompID", "ID"]).size().reset_index(name="counts")  # type: ignore
        db.drop_table(table_name="COMPOSITION_ROLES")
        db.table(
            table_name="COMPOSITION_ROLES",
            columns={"COMPOSITION_ID": "INT", "ROLE_ID": "INT", "COUNT": "INT"},
        )
        for _, row in df_composition_role.iterrows():
            db.execute_query(
                f"""
                INSERT INTO COMPOSITION_ROLES (COMPOSITION_ID, ROLE_ID, COUNT)
                    VALUES ({row[0]}, {row[1]}, {row[2]})
            """
            )
        df_composition_role = db.execute_query("SELECT * FROM COMPOSITION_ROLES")
        print("\n~~~\ndf_composition_role:\n", df_composition_role)

    if df_heroes is not None:
        df_roster = pd.read_csv("hedgebot/modules/utility/hots/data/roster.csv", sep="\t")
        df_roster = pd.merge(df_roster, df_heroes, on="HERO")
        df_roster = df_roster[["USER", "ID"]]
        db.drop_table(table_name="ROSTER")
        db.table(table_name="ROSTER", columns={"USER_ID": "INT", "HERO_ID": "INT"})
        for _, row in df_roster.iterrows():
            db.execute_query(
                f"""
                INSERT INTO ROSTER (USER_ID, HERO_ID)
                    VALUES ({row[0]}, {row[1]})
            """
            )
        df_roster = db.execute_query("SELECT * FROM ROSTER")
        print("\n~~~\ndf_roster:\n", df_roster)
