from discord.ext import commands
import discord

from db import SQLiteManager
from modules.utility.hots.sql import get_user_by_id, get_roster_by_user, put_user


class Commands(commands.Cog):
    """Hero-selection tools for Heroes of the Storm"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.db = SQLiteManager("hedgebot/modules/utility/hots/db.sqlite3")
        self.db.table(table_name="USERS", columns={"USERNAME": "STR", "DISCORD_ID": "INT"})
        self.db.table(table_name="HEROES", columns={"HERO": "TEXT", "STUB": "TEXT", "ROLE_ID": "INT"})
        self.db.table(table_name="ROLES", columns={"ROLE": "TEXT", "ARGUMENT": "TEXT"})
        self.db.table(table_name="ROSTER", columns={"USER_ID": "INT", "HERO_ID": "INT"})
        self.db.table(
            table_name="COMPOSITON",
            columns={"HERO_ID": "INT", "COMPOSITION_ID": "INT", "GAMES": "INT", "SCORE": "REAL"},
        )

    @commands.group(name="Hots", aliases=["HOTS", "HotS", "hots"])
    async def hots(self, ctx: commands.Context) -> None:  # type: ignore
        """Heroes of the Storm commands"""
        if ctx.invoked_subcommand is None:
            await ctx.send_help(self.hots)
        else:
            data = self.db.execute_query(get_user_by_id(ctx.message.author.id))
            if data is None:
                put_user(ctx.message.author.name, ctx.message.author.id)

    @hots.command(name="Roles", aliases=["roles"])
    async def roles(self, ctx: commands.Context):  # type: ignore
        """Outputs a list of the hero roles for use as filters"""
        await ctx.send(
            f"""Ranged Assassin | -r \nMelee Assassin | -m \nTank | -t \nBrusier | -b \nHealer | -h \nSupport | -s"""
        )

    @hots.command(name="Roster", aliases=["roster"])
    @discord.app_commands.describe(role="Date in YYYY-MM-DD format")
    async def roster(self, ctx: commands.Context, *, role: str = ""):  # type: ignore
        """Outputs a list of the heroes in your roster

        Parameters
        -----------
        role: str
            Optional role filter. See 'Roles' command for more information"""
        data = self.db.execute_query(get_roster_by_user(ctx.message.author.id))
        if data is not None:
            hero_list = data["HERO"].to_list()
            await ctx.send(f"{', '.join(hero_list)}")
            return
        await ctx.send(
            f"Hello {ctx.message.author.name}! You do not currently have a Heroes of the Storm roster entered. Use 'Add' to add heroes to your roster"
        )

    @hots.command(name="Draft", aliases=["draft"])
    async def draft(self, ctx: commands.Context, role: str):  # type: ignore
        """Draft a hero from the user's roster.

        Parameters
        -----------
        role: str
            Optional role filter, e.g. "Healer"
        """
        author = str(ctx.message.author.mention)
        await ctx.send(f"Hello, {author}, {role}!")

    #     # Get data
    #     author = str(ctx.message.author.mention)
    #     roster = self.get_roster(author, role)
    #     team = self.get_team()
    #     team = dict((k, str(team[k])) for k in team if k != author)

    #     # Check for records
    #     output = "Unable to select hero"
    #     if roster.shape[0] > 0:

    #         # Import pairings and roles
    #         con = self.get_db()
    #         team_heroes = ""
    #         if len(team) > 1:
    #             team_heroes = f"""
    #             and Duo not in ('{"','".join(list(team.values())[1:])}')
    #             and Hero in ('{"','".join(list(team.values())[1:])}')"""
    #         pairings = pd.read_sql_query(
    #             f"""
    #         select Hero, Duo, Games, Winrate
    #         from Pairings
    #         where Duo in ('{"','".join(roster['Hero'].tolist())}'){team_heroes}""",
    #             con,
    #         )
    #         role_keys = pd.read_sql_query("select Hero, Role from Roster", con)
    #         con.close()

    #         # Adjust win-rate by sample size

    #         # Represented roles
    #         represented_roles = role_keys[role_keys["Hero"].isin(list(team.values()))]["Role"].unique()
    #         represented_roles = pd.DataFrame(represented_roles, columns=["Role"])
    #         represented_roles["role_factor"] = 0.5

    #         # Calculate weights
    #         weights = pd.merge(pairings, role_keys.rename({"Hero": "Duo"}, axis=1), on="Duo")
    #         weights = pd.merge(weights, represented_roles, on="Role", how="left").fillna(1)
    #         weights["factor"] = weights["Winrate"] * weights["role_factor"]
    #         weights = weights.groupby("Duo")["factor"].mean().to_frame("Weight").reset_index()
    #         weights["Weight"] = weights["Weight"] ** 2 * 100 // 1

    #         # Output hero selection
    #         if "optimal" in "".join(role).lower():
    #             output = weights.sort_values(["Weight"], ascending=False)["Duo"].iloc[0]
    #         elif "random" in "".join(role).lower():
    #             output = weights.sample(weights=weights.groupby("Duo")["Weight"].transform("sum"))["Duo"].iloc[0]
    #         else:
    #             output = weights.sample(weights=weights.groupby("Duo")["Weight"].transform("sum"))["Duo"].iloc[0]

    #         # Update team file
    #         self.set_team(team, author, output)

    #     # Output message
    #     await ctx.send(output)

    @hots.command(name="Add", aliases=["add"])
    async def add(self, ctx: commands.Context, *hero):  # type: ignore
        """Add a hero to the users roster

        hero: Name of the hero to add to the users roster
        """
        author = str(ctx.message.author.mention)
        await ctx.send(f"Hello, {author}!")

    @hots.command(name="Remove", aliases=["remove"])
    async def remove(self, ctx: commands.Context, *hero):  # type: ignore
        """Add a hero to the users roster

        hero: Name of the hero to remove from the users roster
        """
        author = str(ctx.message.author.mention)
        await ctx.send(f"Hello, {author}!")

    @hots.command(name="Select", aliases=["select"])
    async def select(self, ctx: commands.Context, *hero):  # type: ignore
        """Add a hero to the users roster

        hero: Name of the hero to add to the current team
        """
        author = str(ctx.message.author.mention)
        await ctx.send(f"Hello, {author}!")

    @hots.command(name="Team", aliases=["team"])
    async def team(self, ctx: commands.Context):  # type: ignore
        """Displays the current team"""
        author = str(ctx.message.author.mention)
        await ctx.send(f"Hello, {author}!")

    @hots.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def clear(self, ctx: commands.Context):  # type: ignore
        """Admin command; Clears current team"""
        author = str(ctx.message.author.mention)
        await ctx.send(f"Hello, {author}!")

    # Backup command - Admin only
    @hots.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def backup(self, ctx: commands.Context):  # type: ignore
        """Admin command; Creates database backup"""
        author = str(ctx.message.author.mention)
        await ctx.send(f"Hello, {author}!")

    @hots.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def etl(self, ctx: commands.Context):  # type: ignore
        """Admin command; Run ETL process to update hero pairing values"""
        author = str(ctx.message.author.mention)
        await ctx.send(f"Hello, {author}!")
