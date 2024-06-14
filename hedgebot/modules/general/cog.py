from discord.ext import commands
import discord
from tools.embed import newembed


class Commands(commands.Cog, name="General"):
    """General purpose commands"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="Ping", aliases=["ping"])
    async def ping(self, ctx: commands.Context) -> None:  # type: ignore
        """
        Check if the bot is alive.

        :param context: The hybrid command context.
        """
        embed = newembed(description=f"🏓 Pong! Hedgebot's latency is {round(self.bot.latency * 1000)}ms.")
        await ctx.send(embed=embed)

    @commands.command(name="id", hidden=True)
    @commands.has_permissions(administrator=True)
    async def id(self, ctx: commands.Context, member: discord.Member):  # type: ignore
        """A command to fetch and return the ID of a mentioned Discord user."""
        await ctx.send(f"{member.mention}'s ID is {member.id}")

    @commands.command(name="Avatar", aliases=["avatar"], hidden=True)
    @commands.has_permissions(administrator=True)
    async def avatar(self, ctx: commands.Context) -> None:  # type: ignore
        """Print avatar url"""
        bot_user = self.bot.user
        avatar_url = bot_user.avatar.url  # type: ignore
        await ctx.send(f"Here is my avatar URL: {avatar_url}")

    @commands.command(name="Admin", aliases=["admin"], hidden=True)
    @commands.has_permissions(administrator=True)
    async def admin(self, ctx: commands.Context):  # type: ignore
        """An admin-only command."""
        await ctx.send("You are my master!")

    @commands.command(name="Admins", aliases=["admins"], hidden=True)
    @commands.has_permissions(administrator=True)
    async def list_admins(self, ctx: commands.Context):  # type: ignore
        """Prints a list of administrators in the server."""
        admins = [member for member in ctx.guild.members if member.guild_permissions.administrator]  # type: ignore

        if not admins:
            await ctx.send("There are no administrators in this server.")
        else:
            admin_list = "\n".join([member.display_name for member in admins])
            await ctx.send(f"Administrators in this server:\n{admin_list}")


async def setup(bot: commands.Bot):
    """Loads cog to hedgebot"""
    await bot.add_cog(Commands(bot))
