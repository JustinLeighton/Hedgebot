import discord
from discord.ext import commands
import os
from config import DISCORD_KEY


class Hedgebot(commands.Bot):
    """Main discord bot object"""

    def __init__(self):
        intents = discord.Intents.all()
        intents.message_content = True
        super().__init__(intents=intents, command_prefix="!")

    async def _load_extension(self):
        """Loads cogs from each module's cog.py file as extensions."""
        for folder in os.listdir("hedgebot/modules"):
            if os.path.exists(os.path.join("hedgebot/modules", folder, "cog.py")):
                await self.load_extension(f"modules.{folder}.cog")

    async def on_ready(self):
        """Prints a message to the terminal indicating that HedgeBot has connected to Discord."""
        print(f"{self.user.name} has connected to Discord.")  # type: ignore[reportOptionalMemberAccess]

    async def do_stuff(self):
        """An asynchronous method that serves as the main event loop of HedgeBot."""
        async with self:
            await self._load_extension()
            await self.start(DISCORD_KEY)
