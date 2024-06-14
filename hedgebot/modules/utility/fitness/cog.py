import discord
from discord import app_commands
from discord.ext import commands
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import sqlite3
from datetime import datetime
import time
from tabulate import tabulate
import random
import os
import typing


class Fitness(commands.Cog):
    """Displays data related to fitness tracking"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.user_map = {"<@271088517424218123>": "Justin", "<@295390092304842753>": "Kenn"}

    @commands.Cog.listener()
    async def on_ready(self):
        print("Fitness loaded")

    @commands.command(name="FitHelp", aliases=["Fithelp", "fithelp"])
    async def fit_help(self, ctx: commands.Context):
        author = str(ctx.message.author.mention)
        if author not in self.user_map.keys():
            await ctx.send(f"You are not a valid user for this command ({author})")
        else:
            await ctx.send("placeholder")

    @commands.command(name="FitData", aliases=["Fitdata", "fitdata"])
    async def fit_data(self, ctx: commands.Context):
        print("Checkpoint #0")
        author = str(ctx.message.author.mention)
        if author not in self.user_map.keys():
            await ctx.send(f"You are not a valid user for this command ({author})")
        else:
            print("Checkpoint #1")
            # Query data
            user = self.user_map[author]
            con = sqlite3.connect("./modules/fitness/db")
            df = pd.read_sql_query(
                f"""
            select a.Item as Exercise
                  ,a.Day
                  ,a.Sets
                  ,a.Reps
                  ,a.Date as LastChanged
                  ,a.Value
            from workout a
            where a.Person = '{user}'
              and a.IsActive = 1""",
                con,
            )
            con.close()
            table = tabulate(df, headers="keys", tablefmt="grid")
            await ctx.send(f"```\n{table}\n```")

    @commands.command(name="FitPlot", aliases=["Fitplot", "fitplot"])
    async def fit_plot(self, ctx: commands.Context, *args):
        author = str(ctx.message.author.mention)
        if author not in self.user_map.keys():
            await ctx.send(f"You are not a valid user for this command ({author})")
        else:
            user = self.user_map[author]
            if len(args) == 0:
                await ctx.send('No exercise selected. Use "!FitHelp" for more information')
            else:
                # Query data
                item = "%".join(args).lower()
                con = sqlite3.connect("./modules/fitness/db")
                df = pd.read_sql_query(
                    f"""
                select a.Item
                      ,'Day ' || a.Day || ', ' || cast(a.Sets as integer) || ' Sets, ' || a.Reps || ' Reps' as Category
                      ,a.Date
                      ,a.Value
                from workout a
                join (select Item from workout where lower(Item) like '%{item}%' limit 1) b on a.Item = b.Item
                where a.Person = '{user}'""",
                    con,
                )
                con.close()
                df["Date"] = pd.to_datetime(df["Date"], format="%Y-%m-%d")

                # Insert record for today
                current = df[df["Date"] == max(df["Date"])].copy()
                current["Date"] = pd.Timestamp.now()
                df = pd.concat([df, current])

                # Create plot
                exercise = df["Item"].iloc[0]
                plot_file = "./modules/fitness/plots/" + str(time.time()).replace(".", "") + ".png"
                for i in df["Category"].unique().tolist():
                    x = df[df["Category"] == i]["Date"]
                    y = df[df["Category"] == i]["Value"]
                    plt.step(x, y, label=i, where="post")
                plt.grid(axis="x", color="0.95")
                plt.legend(title="Category")
                plt.title(f"{user.capitalize()} - {exercise.capitalize()}")
                plt.tick_params(rotation=20)
                plt.savefig(plot_file)

                # Matplotlib Garbage collection
                plt.figure().clear()
                plt.close()
                plt.cla()
                plt.clf()

                # Output image to discord
                with open(plot_file, "rb") as f:
                    image_file = discord.File(f)
                    await ctx.send(file=image_file)


async def setup(bot: commands.Bot):
    await bot.add_cog(Commands(bot))
