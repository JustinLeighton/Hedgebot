import discord

# from config import AVATAR_URL


EMBED_COLOR: int = 0x428DFF


def newembed(c: int = EMBED_COLOR, description: str = "") -> discord.Embed:
    """
    Creates a new Discord embed with a specified color and sets a footer.

    Args:
        c (int): The color of the embed. Defaults to the value of EMBED_COLOR.
        description (str): Text body of embed.

    Returns:
        discord.Embed: A Discord embed object with the specified color and footer.

    The footer includes a text generated by the `copyright` function and an icon URL specified by `AVATAR_URL`.
    """
    em = discord.Embed(colour=c)
    em.set_footer(
        text=description,
        # icon_url=AVATAR_URL,
    )
    return em
