import requests
from discord.ext import commands
from tools.embed import newembed


class Commands(commands.Cog, name="Services"):
    """Tools to generate randomness"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        """Prints a message to the terminal indicating that this module has been loaded."""
        print("Services loaded")

    async def get(self, ctx: commands.Context, url: str) -> any:  # type: ignore
        """Send get request"""
        response = requests.get(url)
        if response.status_code != 200:
            code_description = "Unknown Error"
            try:
                code_description = str(requests.status_codes._codes[response.status_code][0]).replace("_", " ").title()  # type: ignore[reportAttributeAccessIssue]
            except:
                code_description = "Unknown Error"
            finally:
                await ctx.send(f"{response.status_code}: {code_description}")
                return {}
        return response.json()

    @commands.command(name="Cat", aliases=["cat"])
    async def cat(self, ctx: commands.Context):  # type: ignore
        """Get a cat image"""
        response = await self.get(ctx, "https://api.thecatapi.com/v1/images/search")
        if response:
            em = newembed()
            em.set_image(url=response[0]["url"])
            await ctx.send(embed=em)

    # @commands.command(aliases=["woof"])
    # async def dog(self, ctx):
    #     """Get a dog image"""
    #     req = requests.get("http://random.dog/")
    #     if req.status_code != 200:
    #         await ctx.message.add_reaction(emoji="❌")
    #         await ctx.send("API error, could not get a woof")
    #         print("Could not get a woof")
    #     doglink = BeautifulSoup(req.text, "html.parser")
    #     rngdog = "http://random.dog/" + doglink.img["src"]
    #     em = newembed()
    #     em.set_image(url=rngdog)
    #     await ctx.send(embed=em)
    #     await ctx.message.add_reaction(emoji="✅")


async def setup(bot: commands.Bot):
    """Loads cog to hedgebot"""
    await bot.add_cog(Commands(bot))
