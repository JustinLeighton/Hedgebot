def get_user_by_id(discord_id: int) -> str:
    return f"""SELECT * FROM USERS WHERE DISCORD_ID = {discord_id}"""


def get_roster_by_user(discord_id: int) -> str:
    return f"""
            SELECT HERO
            FROM ROSTER
            JOIN USERS ON ROSTER.USER_ID = USERS.ID
            JOIN HEROES ON ROSTER.HERO_ID = HEROES.ID
            WHERE USERS.DISCORD_ID = '{discord_id}'
        """


def put_user(username: str, discord_id: int) -> str:
    return f"""
            INSERT INTO USERS (USERNAME, DISCORD_ID)
            VALUES ('{username}', {discord_id})
        """
