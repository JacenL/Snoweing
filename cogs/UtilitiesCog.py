import discord
from discord.ext import commands
import random
import asyncio
import requests
import re

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
        if not username or not message:
            embed = discord.Embed(title=f"Error", description=f"Please provide a username.", color=discord.Color.red)
            await ctx.reply(embed=embed)
            return
        member = discord.utils.get(ctx.guild.members, name=username)
        if not member:
            member = discord.utils.get(ctx.guild.members, display_name=username)
        if member:
            try:
                await member.send(message)
                embed = discord.Embed(title="Success", description=f"Sent message to {username}.", color=discord.Color.green)
                await ctx.reply(embed=embed)
            except discord.errors.Forbidden:
                embed = discord.Embed(title=f"Error", description=f"Could not send message to {username}. They may have DMs disabled.", color=discord.Color.red)
                await ctx.reply(embed=embed)
            return
        embed = discord.Embed(title=f"Error", description=f"User {username} not found.", color=discord.Color.red)
        await ctx.reply(embed=embed)
    
    @commands.command()
    async def messageping(self, ctx, member:discord.Member, *, message):
        if not message:
            embed = discord.Embed(title=f"Error", description=f"Please type in a message.", color=discord.Color.red)
            await ctx.reply(embed=embed)
            return
        try:
            await member.send(message)
            embed = discord.Embed(title="Success", description=f"Sent message to {member.mention}.", color=discord.Color.green)
            await ctx.reply(embed=embed)
        except discord.errors.Forbidden:
            embed = discord.Embed(title=f"Error", description=f"Could not send message to {member.mention}. They may have DMs disabled.", color=discord.Color.red)
            await ctx.reply(embed=embed)

    @commands.command()
    async def day(self, ctx):
        url = 'https://www.mbhs.edu'
        try:
            await ctx.send("Loading...1")
            response = requests.get(url)
            if response.status_code == 200:
                await ctx.send("Loading...2")
                result = re.search(r"\bTomorrow is an (?:ODD|EVEN) day\b", str(response.text))
                await ctx.send("Loading...3")
                print(result.group())
                embed = discord.Embed(title="Day", description=f"{result.group()}", color=discord.Color.green)
                await ctx.send("Loading...4")
            else:
                embed = discord.Embed(title="Error", description=f"Could not get data from {url}.", color=discord.Color.red)
        except Exception:
            embed = discord.Embed(title="Error", description=f"Something really bad happened.", color=discord.Color.red)
        await ctx.reply(embed=embed)


async def setup(bot):
    await bot.add_cog(UtilitiesCog(bot))
