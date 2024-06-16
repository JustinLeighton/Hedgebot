def get_user_by_id(discord_id: int) -> str:
    return f"""SELECT * FROM USERS WHERE DISCORD_ID = {discord_id}"""


def get_roster_by_user(discord_id: int) -> str:
    return f"""SELECT HERO, ROLE
            FROM ROSTER
            JOIN USERS ON ROSTER.USER_ID = USERS.DISCORD_ID
            JOIN HEROES ON ROSTER.HERO_ID = HEROES.ID
            JOIN ROLES ON HEROES.ROLE_ID = ROLES.ID
            WHERE USERS.DISCORD_ID = {discord_id}
            ORDER BY HERO ASC"""


def post_user(username: str, discord_id: int) -> str:
    return f"""INSERT INTO USERS (USERNAME, DISCORD_ID)
            VALUES ('{username}', {discord_id})"""


def post_roster(discord_id: int, hero_id: int) -> str:
    return f"""INSERT INTO ROSTER (USER_ID, HERO_ID)
            VALUES ({discord_id}, {hero_id})"""


def delete_roster(discord_id: int, hero_id: int) -> str:
    return f"""DELETE FROM ROSTER
            WHERE USER_ID = {discord_id} AND HERO_ID = {hero_id}"""


def get_roles() -> str:
    return "SELECT ROLE, STUB FROM ROLES"


def get_heroes() -> str:
    return """SELECT HEROES.ID, HEROES.HERO, ROLES.ROLE
            FROM HEROES
            JOIN ROLES ON HEROES.ROLE_ID = ROLES.ID"""


def get_roster_by_userid_and_heroid(discord_id: int, hero_id: int) -> str:
    return f"""SELECT HERO
            FROM ROSTER
            WHERE USER_ID = {discord_id} 
            AND HERO_ID = {hero_id}"""
