from discord.ext import commands

from db import SQLiteManager
from modules.utility.fitness.sql import select_user, insert_user, update_user


class Commands(commands.Cog):
    """Displays data related to fitness tracking"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.db = SQLiteManager("hedgebot/modules/utility/fitness/db.sqlite3")
        self.db.table(table_name="USERS", columns={"NAME": "STR"})
        self.db.table(table_name="DATA", columns={"USER_ID": "INT", "NAME": "STR", "INFO": "STR", "VALUE": "REAL"})
        self.db.table(table_name="SCHEDULE", columns={"USER_ID": "INT", "DATA_ID": "INT", "DAY": "INT"})

    @commands.Cog.listener()
    async def on_ready(self):
        print("Fitness loaded")

    @commands.group(name="Fitness", aliases=["fitness", "Fit", "fit"])
    async def fitness(self, ctx: commands.Context) -> None:  # type: ignore
        """Fitness commands"""
        if ctx.invoked_subcommand is None:
            await ctx.send_help(self.fitness)

    @fitness.command(name="user")
    @commands.has_permissions(administrator=True)
    async def user(self, ctx: commands.Context, id: int, user: str):  # type: ignore
        data = self.db.execute_query(select_user(id))
        query, message = (insert_user, "added with") if data is None else (update_user, "updated to")
        self.db.execute_query(query(id, user))
        await ctx.send(f"{id} {message} name: {user}")




async def setup(bot: commands.Bot):
    await bot.add_cog(Commands(bot))
