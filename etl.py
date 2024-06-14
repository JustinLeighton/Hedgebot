import hashlib

import pandas as pd

from hedgebot.db import SQLiteManager


db = SQLiteManager("hedgebot/modules/utility/hots/db.sqlite3")


def get_hash(input_string: str, length: int = 8):
    hash_object = hashlib.sha256()
    hash_object.update(input_string.encode("utf-8"))
    hash_str = hash_object.hexdigest()
    short_hash = hash_str[:length]
    hash_int = int(short_hash, 16)
    return hash_int


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
print(df_roles)

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
    print(df_heroes)

# https://www.heroesprofile.com/Global/Compositions?timeframe_type=major&timeframe=2.55&game_type=qm&hero=Abathur
df = pd.read_csv("hedgebot/modules/utility/hots/data/composition.csv", sep="\t", header=False)
db.drop_table(table_name="COMPOSITION")
db.table(
    table_name="COMPOSITON",
    columns={"HERO_ID": "INT", "GAMES": "INT", "SCORE": "REAL"},
)

# # https://www.heroesprofile.com/Global/Compositions?timeframe_type=major&timeframe=2.55&game_type=qm&hero=Abathur
# df = pd.read_csv("hedgebot/modules/utility/hots/data/composition.csv", sep="\t", header=False)
# db.drop_table(table_name="COMPOSITION_ROLES")
# db.table(
#     table_name="COMPOSITON_ROLES",
#     columns={"COMPOSITION_ID": "INT", "ROLE_ID": "INT", "COUNT": "INT"},
# )

# # df = pd.read_csv("hedgebot/modules/utility/hots/data/users_backup.csv", sep="\t", header=False)
# db.drop_table(table_name="USERS")
# db.table(table_name="USERS", columns={"USERNAME": "STR", "DISCORD_ID": "INT"})

# # df = pd.read_csv("hedgebot/modules/utility/hots/data/roster_backup.csv", sep="\t", header=False)
# db.drop_table(table_name="ROSTER")
# db.table(table_name="ROSTER", columns={"USER_ID": "INT", "HERO_ID": "INT"})
