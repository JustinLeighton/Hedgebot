import random
from sqlite3 import IntegrityError

import aiohttp
import pandas as pd
from discord.ext import commands

from tools.embed import newembed
from db import SQLiteManager


class Commands(commands.Cog, name="Random"):
    """Tools to generate randomness"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.db = SQLiteManager("hedgebot/modules/random/db.sqlite3")
        self.db.table(table_name="EIGHTBALL", columns={"RESPONSE": "TEXT UNIQUE"})
        # file = open("./hedgebot/modules/random/8ball_responses.txt", "r")
        # data = file.read()
        # self._8ball_responses = data.split("\n")

    @commands.Cog.listener()
    async def on_ready(self):
        """Prints a message to the terminal indicating that this module has been loaded."""
        print("Random loaded")

    @commands.command(name="Ask", aliases=["ask"])
    async def ask(self, ctx: commands.Context, *, question: str):  # type: ignore
        """Ask Hedgebot a yes/no question"""
        answer = self.db.execute_query("SELECT `RESPONSE` FROM EIGHTBALL ORDER BY RANDOM() LIMIT 1")
        if type(answer) is pd.DataFrame:
            answer_string = str(answer["RESPONSE"].iloc[0])  # type: ignore
            await ctx.send(f"Question: {question}\nAnswer: {answer_string}")
        else:
            await ctx.send("No available responses")

    @commands.command(name="Choose", aliases=["choose"])
    async def choose(self, ctx: commands.Context, *args: list[str]):  # type: ignore
        """Give Hedgebot a list of items to choose from"""
        await ctx.send(f"{random.choice(args)}")

    @commands.hybrid_command(name="fact", aliases=["Fact"])
    async def fact(self, context: commands.Context) -> None:  # type: ignore
        """Get a random fact."""
        # This will prevent your bot from stopping everything when doing a web request - see: https://discordpy.readthedocs.io/en/stable/faq.html#how-do-i-make-a-web-request
        async with aiohttp.ClientSession() as session:
            async with session.get("https://uselessfacts.jsph.pl/api/v2/facts/random") as request:
                if request.status == 200:
                    data = await request.json()
                    embed = newembed(description=data["text"])
                else:
                    embed = newembed(description="Error!")
                await context.send(embed=embed)

    @commands.command("ask_add", hidden=True)
    @commands.has_permissions(administrator=True)
    async def ask_add(self, ctx: commands.Context, *, text_response: str):  # type: ignore
        """Insert text into 8ball pool of responses"""
        try:
            self.db.insert_row("EIGHTBALL", (None, text_response))
            await ctx.send(f"Added: {text_response}")
        except IntegrityError:
            await ctx.send("Response already exists.")

    @commands.command("ask_remove", hidden=True)
    @commands.has_permissions(administrator=True)
    async def ask_remove(self, ctx: commands.Context, *, text_response: str):  # type: ignore
        """Remove text from 8ball pool of responses"""
        try:
            self.db.delete_row("EIGHTBALL", f"RESPONSE = '{text_response}'")
            await ctx.send(f"Removed: {text_response}")
        except IntegrityError:
            await ctx.send("Response does not exist.")

    @commands.command("ask_all", hidden=True)
    @commands.has_permissions(administrator=True)
    async def ask_all(self, ctx: commands.Context):  # type: ignore
        """Output all responses in the 8ball pool"""
        responses = self.db.execute_query("SELECT `RESPONSE` FROM EIGHTBALL")
        if type(responses) is pd.DataFrame:
            formatted_responses = "\n".join(row for row in responses["RESPONSE"])  # type: ignore
            await ctx.send(f"All responses:\n{formatted_responses}")
        else:
            await ctx.send("No available responses")


async def setup(bot: commands.Bot):
    """Loads cog to hedgebot"""
    await bot.add_cog(Commands(bot))
