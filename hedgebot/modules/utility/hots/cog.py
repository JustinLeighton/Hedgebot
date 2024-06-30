from datetime import datetime, timedelta
import random

from discord.ext import commands
import discord
from pandas import DataFrame

from db import SQLiteManager
from tools.utils import cosine_similarity_ngrams, sanitize_string, safe_cast_to_int
from tools.embed import newembed
from modules.utility.hots.sql import (
    select_user_by_id,
    select_roster_by_user,
    select_roles,
    select_roster_by_userid_and_heroid,
    select_heroes,
    select_team,
    select_team_by_userid,
    select_composition_stats,
    insert_user,
    insert_roster,
    insert_team,
    update_team,
    delete_team,
    delete_roster,
)
from modules.utility.hots.etl import run_hots_etl
from modules.utility.hots.data.hero_selection import HERO_SELECTION_MESSAGES


class Commands(commands.Cog):
    """Hero-selection tools for Heroes of the Storm"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.db = SQLiteManager("hedgebot/modules/utility/hots/db.sqlite3")
        self.db.table(table_name="USERS", columns={"USERNAME": "STR"})
        self.db.table(table_name="HEROES", columns={"HERO": "TEXT", "STUB": "TEXT", "ROLE_ID": "INT"})
        self.db.table(table_name="ROLES", columns={"ROLE": "TEXT", "ARGUMENT": "TEXT"})
        self.db.table(table_name="ROSTER", columns={"USER_ID": "INT", "HERO_ID": "INT"})
        self.db.table(table_name="TEAM", columns={"USER_ID": "INT", "HERO_ID": "INT"})
        self.db.table(
            table_name="COMPOSITION",
            columns={"HERO_ID": "INT", "COMPOSITION_ID": "INT", "GAMES": "INT", "SCORE": "REAL"},
        )

        self.team_timestamp: datetime = datetime.now()
        self.team_time_minutes: int = 10

    @commands.group(name="Hots", aliases=["HOTS", "HotS", "hots"])
    async def hots(self, ctx: commands.Context) -> None:  # type: ignore
        """Heroes of the Storm commands"""
        if ctx.invoked_subcommand is None:
            await ctx.send_help(self.hots)
        else:
            query = select_user_by_id(ctx.message.author.id)
            data = self.db.execute_query(query)
            if data is None:
                query = insert_user(ctx.message.author.id, ctx.message.author.name.title())
                self.db.execute_query(query)

    @hots.command(name="Roles", aliases=["roles", "Role", "role"])
    async def roles(self, ctx: commands.Context):  # type: ignore
        """Outputs a list of the hero roles for use as filters"""
        query = select_roles()
        data = self.db.execute_query(query)
        if data is not None:
            embed = newembed()
            embed.add_field(name="Role", value="\n".join(list(data["ROLE"])), inline=True)
            embed.add_field(name="Stub", value="\n".join(list(data["STUB"])), inline=True)
            await ctx.send(embed=embed)

    @hots.command(name="Roster", aliases=["roster"])
    async def roster(self, ctx: commands.Context, *, role: str = ""):  # type: ignore
        """Outputs a list of the heroes in your roster

        Parameters
        -----------
        role: str
            stubs (see 'Role')."""
        query = select_roster_by_user(ctx.message.author.id)
        data = self.db.execute_query(query)
        if data is not None:
            embed = self.get_hero_table_embed(data, f"{ctx.message.author.name.title()}'s Roster")
            await ctx.send(embed=embed)
            return
        await ctx.send(
            f"Hello {ctx.message.author.name}! You do not currently have a Heroes of the Storm roster entered. Use 'Add' to add heroes to your roster"
        )

    @hots.command(name="Draft", aliases=["draft"])
    async def draft(self, ctx: commands.Context, *role: str):  # type: ignore
        """Draft a hero from the user's roster using weighted-random selection.

        Parameters
        -----------
        role: str
            stubs (see 'Role'), '-o' for optimal, '-x' for completely random."""
        self.check_team_timer()

        # Validate role filters, and check for optimal flag here
        # ~~~
        # ~~~
        # ~~~

        # Get data
        discord_id, username = ctx.message.author.id, ctx.message.author.name.title()
        query = select_composition_stats(discord_id, role)
        data = self.db.execute_query(query)

        # Make selection
        if data is not None:
            selection = data[["HERO_ID", "HERO"]].sample().iloc[0]  # sample has a weights argument
            await self.post_hero_selection(ctx, discord_id, username, selection["HERO_ID"], selection["HERO"])

    @hots.command(name="Add", aliases=["add"])
    async def add(self, ctx: commands.Context, *hero):  # type: ignore
        """Add a hero to the user's roster

        Parameters
        -----------
        hero: str
            Name of the hero to add to the users roster
        """
        hero_name, hero_id = await self.fuzzy_match_hero_name(ctx, " ".join(hero))
        if hero_id > -1:
            query = select_roster_by_userid_and_heroid(ctx.message.author.id, hero_id)
            data = self.db.execute_query(query)

            if data is not None:
                await ctx.send(f"Already have {hero_name} in your roster!")
                return

            query = insert_roster(ctx.message.author.id, hero_id)
            data = self.db.execute_query(query)
            await ctx.send(f"Added {hero_name} to your roster!")

    @hots.command(name="Remove", aliases=["remove"])
    async def remove(self, ctx: commands.Context, *hero):  # type: ignore
        """Remove a hero to the user's roster

        Parameters
        -----------
        hero: str
            Name of the hero to add to the users roster
        """
        hero_name, hero_id = await self.fuzzy_match_hero_name(ctx, " ".join(hero))
        if hero_id > -1:
            query = select_roster_by_userid_and_heroid(ctx.message.author.id, hero_id)
            data = self.db.execute_query(query)

            if data is None:
                await ctx.send(f"You don't have {hero_name} in your roster!")
                return

            query = delete_roster(ctx.message.author.id, hero_id)
            data = self.db.execute_query(query)
            await ctx.send(f"Removed {hero_name} to your roster!")

    @hots.command(name="Select", aliases=["select"])
    async def select(self, ctx: commands.Context, *hero):  # type: ignore
        """Choose a hero to the current team

        Parameters
        -----------
        hero: str
            Name of the hero to add to the users roster
        """
        self.check_team_timer()
        hero_name, hero_id = await self.fuzzy_match_hero_name(ctx, " ".join(hero))
        discord_id, username = ctx.message.author.id, ctx.message.author.name.title()
        if hero_id > -1:
            await self.post_hero_selection(ctx, discord_id, username, hero_id, hero_name)

    @hots.command(name="Team", aliases=["team"])
    async def team(self, ctx: commands.Context):  # type: ignore
        """Displays the current team"""
        self.check_team_timer()
        query = select_team()
        data = self.db.execute_query(query)
        if data is not None:
            embed = newembed()
            embed.add_field(name="Player", value="\n".join(list(data["USERNAME"])))
            embed.add_field(name="Hero", value="\n".join(list(data["HERO"])))
            embed.add_field(name="Role", value="\n".join(list(data["ROLE"])))
            await ctx.send(embed=embed)
        else:
            await ctx.send("No current team found")

    @hots.command(name="Hero", aliases=["hero", "Heroes", "heroes"])
    async def hero(self, ctx: commands.Context):  # type: ignore
        """Displays all available heroes"""
        query = select_heroes()
        data = self.db.execute_query(query)
        if data is not None:
            embed = self.get_hero_table_embed(data, "Available Heroes")
            await ctx.send(embed=embed)
            return
        await ctx.send(f"Something went wrong; No heroes available...")

    @hots.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def clear(self, ctx: commands.Context):  # type: ignore
        """Admin command; Clears current team"""
        query = delete_team()
        self.db.execute_query(query)
        await ctx.send(f"Team cleared!")

    @hots.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def backup(self, ctx: commands.Context):  # type: ignore
        """Admin command; Creates database backup"""
        await ctx.send(f"501: Not implemented")

    @hots.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def etl(self, ctx: commands.Context):  # type: ignore
        """Admin command; Run ETL process to update hero pairing values"""
        run_hots_etl()
        await ctx.send(f"HotS ETL finished!")

    @hots.command(name="fuzzy", hidden=True)
    async def fuzzy(self, ctx: commands.Context, *hero):  # type: ignore
        """Admin command; Run ETL process to update hero pairing values"""
        hero = " ".join(hero)
        match, id = await self.fuzzy_match_hero_name(ctx, hero)
        if id > -1:
            await ctx.send(f"{hero} matched to {match} with ID {id}")

    def check_team_timer(self):
        """Checks if enough time has passed to start a new team"""
        current_time = datetime.now()
        time_difference = current_time - self.team_timestamp
        if time_difference >= timedelta(minutes=5):
            query = delete_team()
            self.db.execute_query(query)
        self.team_timestamp = datetime.now()

    def get_hero_table_embed(self, data: DataFrame, title: str) -> discord.Embed:
        """
        Generates a Discord embed displaying heroes categorized by roles.

        Args:
            data (DataFrame): DataFrame containing hero-role mappings.
            title (str): Title for the embed.

        Returns:
            discord.Embed: Embed object containing categorized hero information.
        """
        embed = newembed(title=title)
        roles = self.db.execute_query("SELECT ROLE FROM ROLES")
        if roles is not None:
            roles = list(roles["ROLE"])
            for role in roles:
                embed.add_field(name=role, value=", ".join(list(data[data["ROLE"] == role]["HERO"])))
        return embed

    async def post_hero_selection(self, ctx: commands.Context, discord_id: int, username: str, hero_id: int, hero_name: str):  # type: ignore
        query = select_team_by_userid(discord_id)
        data = self.db.execute_query(query)
        query = insert_team(discord_id, hero_id) if data is None else update_team(discord_id, hero_id)
        self.db.execute_query(query)
        message = self.get_hero_selection_message(ctx.message.author.name, hero_name)
        await ctx.send(message)

    def get_hero_selection_message(self, username: str, heroname: str) -> str:
        message_template = random.choice(HERO_SELECTION_MESSAGES)
        return message_template.format(username=username, heroname=heroname)

    async def fuzzy_match_hero_name(self, ctx: commands.Context, input: str, threshold: float = 0.5) -> tuple[str, int]:  # type: ignore
        """
        Performs a fuzzy matching of input against a list of hero names.

        Args:
            ctx (commands.Context): Context object for sending messages.
            input (str): Input string to be matched against hero names.
            threshold (float, optional): Similarity threshold for fuzzy matching. Defaults to 0.5.

        Returns:
            tuple[str, int]: A tuple containing the matched hero name and its ID,
                            or an empty string and -1 if no match is found.
        """
        query = select_heroes()
        data = self.db.execute_query(query)
        while data is not None:

            input = sanitize_string(input)
            heroes = [sanitize_string(hero) for hero in list(data["HERO"])]
            match, best = "", 0

            for hero in heroes:
                score = cosine_similarity_ngrams(hero, input)
                if score > best:
                    match, best = hero, score

            try:
                idx = heroes.index(match)
            except Exception:
                break

            id = safe_cast_to_int(data["ID"].iloc[idx])
            hero_match = data["HERO"].iloc[idx]
            if id == -1 or best < threshold:
                break

            return hero_match, id

        await ctx.send(f"'{input}' didn't match to any available heroes... Use 'Hero' to see list of available heroes.")
        return "", -1
