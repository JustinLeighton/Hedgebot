from discord.ext import commands
from modules.utility.hots import Hots  # pylint: disable=no-name-in-module
from modules.utility.fitness import Fitness  # type: ignore


class Commands(Hots, Fitness, name="Utility"):
    """Commands for tabletop role-playing games"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        super().__init__(bot)

    @commands.Cog.listener()
    async def on_ready(self):
        """Prints a message to the terminal indicating that this module has been loaded."""
        print("Utility loaded")

    @commands.command(name="Test", aliases=["test"])
    async def test(self, ctx: commands.Context):  # type: ignore
        """Placeholder command"""
        await ctx.send(f"Pong! {round(self.bot.latency * 1000)}ms")


async def setup(bot: commands.Bot):
    """Loads cog to hedgebot"""
    await bot.add_cog(Commands(bot))
