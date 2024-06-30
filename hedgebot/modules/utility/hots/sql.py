def select_user_by_id(discord_id: int) -> str:
    return f"""SELECT * FROM USERS WHERE ID = {discord_id}"""


def select_roster_by_user(discord_id: int) -> str:
    return f"""SELECT ROSTER.HERO_ID, HEROES.HERO, ROLES.ROLE
            FROM ROSTER
            JOIN USERS ON ROSTER.USER_ID = USERS.ID
            JOIN HEROES ON ROSTER.HERO_ID = HEROES.ID
            JOIN ROLES ON HEROES.ROLE_ID = ROLES.ID
            WHERE USERS.ID = {discord_id}
            ORDER BY HERO ASC"""


def select_roles() -> str:
    return "SELECT ROLE, STUB FROM ROLES"


def select_heroes() -> str:
    return """SELECT HEROES.ID, HEROES.HERO, ROLES.ROLE
            FROM HEROES
            JOIN ROLES ON HEROES.ROLE_ID = ROLES.ID"""


def select_roster_by_userid_and_heroid(discord_id: int, hero_id: int) -> str:
    return f"""SELECT HERO_ID
            FROM ROSTER
            WHERE USER_ID = {discord_id} 
            AND HERO_ID = {hero_id}"""


def select_team() -> str:
    return """SELECT TEAM.USER_ID, USERS.USERNAME, TEAM.HERO_ID, HEROES.HERO, ROLES.ROLE, HEROES.ROLE_ID
            FROM TEAM
            JOIN USERS ON TEAM.USER_ID = USERS.ID
            JOIN HEROES ON TEAM.HERO_ID = HEROES.ID
            JOIN ROLES ON HEROES.ROLE_ID = ROLES.ID"""


def select_team_by_userid(discord_id: int) -> str:
    return f"""SELECT HERO_ID FROM TEAM WHERE USER_ID = {discord_id}"""


def select_composition_stats(discord_id: int, role_stubs: tuple[str, ...]) -> str:
    query = f"""WITH ROLECOUNT AS (
                SELECT ROLES.ID AS ROLE_ID, COUNT(TEAM.HERO_ID) AS ROLE_N
                FROM ROLES
                JOIN HEROES ON ROLES.ID = HEROES.ROLE_ID
                LEFT JOIN TEAM ON HEROES.ID = TEAM.HERO_ID AND TEAM.USER_ID != {discord_id}
                GROUP BY ROLES.ID
            ),
            COMP AS (
            SELECT COMPOSITION.ID
                ,COMPOSITION.HERO_ID
                ,COMPOSITION.GAMES AS COMP_GAMES
                ,COMPOSITION.SCORE AS COMP_SCORE
            FROM COMPOSITION
            LEFT JOIN TEAM ON COMPOSITION.HERO_ID = TEAM.HERO_ID AND TEAM.USER_ID != {discord_id}
            JOIN ROSTER ON COMPOSITION.HERO_ID = ROSTER.HERO_ID AND ROSTER.USER_ID = {discord_id}
            JOIN HEROES ON ROSTER.HERO_ID = HEROES.ID
            CROSS JOIN ROLECOUNT
            LEFT JOIN COMPOSITION_ROLES ON COMPOSITION.ID = COMPOSITION_ROLES.COMPOSITION_ID AND ROLECOUNT.ROLE_ID = COMPOSITION_ROLES.ROLE_ID
            WHERE TEAM.HERO_ID IS NULL
            AND IFNULL(COMPOSITION_ROLES.COUNT,0) != ROLECOUNT.ROLE_N
            GROUP BY COMPOSITION.ID, COMPOSITION.HERO_ID, COMPOSITION.GAMES, COMPOSITION.SCORE
            HAVING MIN(IFNULL(COMPOSITION_ROLES.COUNT,0) - ROLECOUNT.ROLE_N) > 0
            )
            SELECT COMP.*, HEROES.HERO, HEROES.GAMES AS HERO_GAMES, HEROES.WINRATE AS HERO_SCORE
            FROM COMP
            JOIN HEROES ON COMP.HERO_ID = HEROES.ID
            JOIN ROLES ON HEROES.ROLE_ID = ROLES.ID
            """
    if role_stubs:
        query += f"""\nWHERE ROLES.STUB IN ('{"','".join(role_stubs)}')"""
    return query


def insert_user(discord_id: int, username: str) -> str:
    return f"""INSERT INTO USERS (ID, USERNAME)
            VALUES ({discord_id}, '{username}')"""


def insert_team(discord_id: int, hero_id: int) -> str:
    return f"""INSERT INTO TEAM (USER_ID, HERO_ID)
            VALUES ({discord_id}, {hero_id})"""


def insert_roster(discord_id: int, hero_id: int) -> str:
    return f"""INSERT INTO ROSTER (USER_ID, HERO_ID)
            VALUES ({discord_id}, {hero_id})"""


def update_team(discord_id: int, hero_id: int) -> str:
    return f"""UPDATE TEAM 
            SET HERO_ID = {hero_id} 
            WHERE USER_ID = {discord_id}"""


def delete_roster(discord_id: int, hero_id: int) -> str:
    return f"""DELETE FROM ROSTER
            WHERE USER_ID = {discord_id} AND HERO_ID = {hero_id}"""


def delete_team() -> str:
    return "DELETE FROM TEAM"
