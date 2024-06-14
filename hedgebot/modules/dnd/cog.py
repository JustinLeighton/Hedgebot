from discord.ext import commands
import random
from datetime import datetime, timedelta
import re
import aiohttp
from typing import Any


async def post_request(url: str, json: dict[str, Any]) -> aiohttp.ClientResponse:
    """
    Sends an asynchronous POST request to the specified URL with the provided data.

    Args:
        url (str): The URL to which the POST request is sent.
        json (dict[str, Any]): The JSON data to be included in the POST request.

    Returns:
        aiohttp.ClientResponse: The response object returned from the POST request.
    """
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=json) as response:
            return response


class Commands(commands.Cog, name="D&D"):
    """General purpose commands"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.mixmancer_url = ""
        self.connection_time = datetime(1900, 1, 1, 0, 0)
        self.hours = 4
        self.dice_template = {
            "d4": 0,
            "d6": 0,
            "d8": 0,
            "d10": 0,
            "d12": 0,
            "d20": 0,
            "d100": 0,
            "modifier": 0,
            "advantage": False,
            "disadvantage": False,
        }

    @commands.Cog.listener()
    async def on_ready(self):
        """Prints a message to the terminal indicating that this module has been loaded."""
        print("D&D loaded")

    async def update_connection_time(self, reset: bool = False):
        """Resets connection_time"""
        self.connection_time = datetime.now() if reset else datetime(1900, 1, 1, 0, 0)

    async def parse_url(self, url: str) -> str:
        """Parse and validate the URL, ensuring it includes http/https scheme."""
        url_regex = re.compile(
            r"^(https?://)?"  # optional http or https scheme
            r"((([a-zA-Z0-9-_]+\.)+[a-zA-Z]{2,})|"  # domain name
            r"(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}))"  # or IPv4 address
            r"(:\d+)?(/.*)?$"  # optional port and path
        )

        # Prepend http:// if no scheme is provided
        if not url.startswith("http://") and not url.startswith("https://"):
            url = "http://" + url

        if not url_regex.match(url):
            raise ValueError("Invalid URL or IP address.")

        return url

    async def parse_roll(self, text: str) -> dict[str, Any]:
        """Parse the roll command text into a dictionary"""
        data = self.dice_template.copy()

        # Regex to find dice rolls and modifiers
        dice_regex = re.compile(r"(\d+)?d(\d+)|([-+]\d+)")
        advantage_regex = re.compile(r"adv", re.IGNORECASE)
        disadvantage_regex = re.compile(r"dis", re.IGNORECASE)

        for match in dice_regex.finditer(text):  # Modifier
            if match.group(3):
                data["modifier"] += int(match.group(3))
            else:  # Dice type
                num_dice = int(match.group(1)) if match.group(1) else 1
                dice_type = f"d{match.group(2)}"
                if dice_type in data:
                    data[dice_type] += num_dice

        if disadvantage_regex.search(text):
            data["disadvantage"] = True
        elif advantage_regex.search(text):
            data["advantage"] = True

        return data

    async def roll_dice(self, data: dict[str, Any]) -> str:
        """Rolls any number of any-sided dice"""
        rolls: list[int] = []
        total: int = 0
        modifier: int = data["modifier"]

        for dice_type, count in data.items():
            if dice_type.startswith("d") and count > 0:
                sides = int(dice_type[1:])
                rolls += [random.randint(1, sides) for _ in range(count)]

        agg_function = max if data["advantage"] else (min if data["disadvantage"] else sum)
        total = agg_function(rolls) + modifier
        response = f"{total}, rolling {', '.join([str(x) for x in rolls])}"

        return response

    @commands.command(name="connect", hidden=True)
    @commands.has_permissions(administrator=True)
    async def connect(self, ctx: commands.Context, *, url: str):  # type: ignore
        """Checks for a response from the bot"""
        try:
            url = await self.parse_url(url)
        except ValueError as e:
            await ctx.send(str(e))
            return

        await self.update_connection_time(reset=True)
        self.mixmancer_url = url
        await ctx.send(f"Connected to {url}")

    @commands.command(name="connection", hidden=True)
    @commands.has_permissions(administrator=True)
    async def connection(self, ctx: commands.Context):  # type: ignore
        """Check existing connection"""
        await ctx.send(f"Connection: {self.mixmancer_url}\nTime: {self.connection_time}")

    @commands.command(name="Roll", aliases=["roll"])
    async def roll(self, ctx: commands.Context, *, text: str = None):  # type: ignore
        """Rolls any number of any-sided dice"""

        # Missing argument
        if not text:
            await ctx.send("Usage: !roll <number of dice>d<number of sides> [e.g., !roll 2d6]")
            return

        # Parse input
        data = await self.parse_roll(text)
        if data == self.dice_template:
            await ctx.send("Usage: !roll <number of dice>d<number of sides> [e.g., !roll 2d6]")
            return

        # Remote roll
        now = datetime.now()
        time_delta = now - self.connection_time <= timedelta(hours=self.hours)
        if time_delta and self.mixmancer_url:
            response = await post_request(url=self.mixmancer_url, json=data)
            if response.status == 200:
                await ctx.send(f"Sending roll to mixmancer...")
                return

        # Local roll
        result = await self.roll_dice(data)
        await ctx.send(result)


async def setup(bot: commands.Bot):
    """Loads cog to hedgebot"""
    await bot.add_cog(Commands(bot))
