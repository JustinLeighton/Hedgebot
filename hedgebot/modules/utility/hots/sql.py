def get_user_by_id(discord_id: int) -> str:
    return f"""SELECT * FROM USERS WHERE DISCORD_ID = {discord_id}"""


def get_roster_by_user(discord_id: int) -> str:
    return f"""
            SELECT HERO, ROLE
            FROM ROSTER
            JOIN USERS ON ROSTER.USER_ID = USERS.DISCORD_ID
            JOIN HEROES ON ROSTER.HERO_ID = HEROES.ID
            JOIN ROLES ON HEROES.ROLE_ID = ROLES.ID
            WHERE USERS.DISCORD_ID = {discord_id}
            ORDER BY HERO ASC
        """


def put_user(username: str, discord_id: int) -> str:
    return f"""
            INSERT INTO USERS (USERNAME, DISCORD_ID)
            VALUES ('{username}', {discord_id})
            
        """


def get_roles() -> str:
    return "SELECT ROLE, STUB FROM ROLES"
