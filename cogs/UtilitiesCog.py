import discord
from discord.ext import commands
import random
import asyncio

class UtilitiesCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def ping(self, ctx):
        embed = discord.Embed(title=f"Pong! Latency: {round(self.bot.latency * 1000)}ms", color=discord.Color.blue())
        await ctx.reply(embed=embed)

    @commands.command(aliases=['8ball'])
    async def eightball(self, ctx, *, question):
        responses = ["No lol", "Jason sucks at coding, try again later", "Not happening", "Yeah sure.", "Get your serve in first before asking me", "Why u ask me", "Probably...", "idk, i dont have the imagination to think of more responses, help me out.", "It is certain", "It is decidedly so", "Without a doubt", "Yes definitely", "My reply is no", "Outlook not so good", "Don’t count on it", "As I see it, yes", "Outlook good", "Signs point to yes"]
        embed = discord.Embed(title=f"**Question: ** {question}\n**Answer: ** {random.choice(responses)}", color=discord.Color.blue())
        await ctx.reply(embed=embed)

    @commands.command()
    async def clear(self, ctx, amount = 0):
        await ctx.channel.purge(limit = amount+1)
        embed = discord.Embed(title=f"Cleared {amount} Messages", color=discord.Color.green())
        await ctx.send(embed=embed)

    @commands.command()
    async def coinflip(self, ctx):
        embed1 = discord.Embed(title="Flipping...", color=discord.Color.blue())
        message = await ctx.reply(embed=embed1)
        await asyncio.sleep(2)
        embed2 = discord.Embed(title=f"{random.choice(['Heads!', 'Tails!'])}", color=discord.Color.green())
        await message.edit(embed=embed2)

    @commands.command()
    async def die(self, ctx):
        await ctx.reply("dying...dead")
        await self.bot.close()

    @commands.command()
    async def message(self, ctx, username, *, message):
        if username == None:
            embed = discord.Embed("Please provide a username", color=discord.Color.red)
            await ctx.reply(embed=embed)
        for member in ctx.guild.members:
            if member.name == username:
                await ctx.guild.get_member_named(username).send(message)
                embed = discord.Embed(title=f"Sent message to {username}.", color=discord.Color.red)
                await ctx.reply(embed=embed)
                return
        embed = discord.Embed(title=f"User {username} not found.", color=discord.Color.red)
        await ctx.reply(embed=embed)

async def setup(bot):
    await bot.add_cog(UtilitiesCog(bot))
