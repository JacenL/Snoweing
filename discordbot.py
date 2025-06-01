import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

load_dotenv()

bot = commands.Bot(command_prefix="-", intents=discord.Intents.all())

extensions = ["cogs.ModerationCog", "cogs.UtilitiesCog", "cogs.HypixelTrackingCog"]

async def loadCogs():
    for file in os.listdir("./cogs"):
        if file.endswith(".py"):
            try:
                await bot.load_extension(f"cogs.{file[:-3]}")
            except Exception as e:
                print(f"Failed to load cog {file}: {e}")

@bot.event
async def on_ready():
    await loadCogs()
    print("Frostfall is online!")

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, discord.ext.commands.errors.CommandNotFound):
        embed = discord.Embed(title="You probably typed something wrong or that command doesn't exist", color=discord.Color.blue())
        await ctx.reply(embed=embed)

bot.run(os.getenv("botToken"))
