def select_user(discord_id: int) -> str:
    return f"""SELECT * FROM USERS WHERE ID = {discord_id}"""


def insert_user(discord_id: int, name: str) -> str:
    return f"""INSERT INTO USERS (ID, NAME)
            VALUES ({discord_id}, '{name}')"""


def update_user(discord_id: int, name: str) -> str:
    return f""""""
