import discord
from discord.ext import commands
from datetime import datetime, timedelta
import random
import asyncio
import requests
import re

class UtilitiesCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.ownerID = 535893497388204047

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
    @commands.has_guild_permissions(manage_messages=True)
    async def clear(self, ctx, amount = 0):
        if amount >= 5 and ctx.author.id != self.ownerID:
            amount = 5
            await ctx.channel.purge(limit = amount+1)
        else:
            await ctx.channel.purge(limit = amount+1)
        embed = discord.Embed(title=f"Cleared {amount} Messages", color=discord.Color.green())
        await ctx.send(embed=embed)
    
    @clear.error
    async def clear_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            embed = discord.Embed(title="No Perms >:D", color=discord.Color.blue())
            await ctx.reply(embed=embed)
        else:
            embed = discord.Embed(title="You idiot you typed the command wrong", color=discord.Color.blue())
            await ctx.reply(embed=embed)

    @commands.command()
    async def coinflip(self, ctx):
        embed = discord.Embed(title="Flipping...", color=discord.Color.blue())
        message = await ctx.reply(embed=embed)
        await asyncio.sleep(2)
        embed = discord.Embed(title=f"{random.choice(['Heads!', 'Tails!'])}", color=discord.Color.green())
        await message.edit(embed=embed)

    @commands.command()
    async def message(self, ctx, username, *, message):
        if not username or not message:
            embed = discord.Embed(title=f"Error", description=f"Please provide a username.", color=discord.Color.red())
            await ctx.reply(embed=embed)
            return
        member = discord.utils.get(ctx.guild.members, name=username)
        if not member:
            member = discord.utils.get(ctx.guild.members, display_name=username)
        if member:
            try:
                await member.send(message)
                embed = discord.Embed(title="Success", description=f"Sent message to {username}.", color=discord.Color.green())
                await ctx.reply(embed=embed)
            except discord.errors.Forbidden:
                embed = discord.Embed(title=f"Error", description=f"Could not send message to {username}. They may have DMs disabled.", color=discord.Color.red())
                await ctx.reply(embed=embed)
            return
        embed = discord.Embed(title=f"Error", description=f"User {username} not found.", color=discord.Color.red())
        await ctx.reply(embed=embed)
    
    @commands.command()
    async def messageping(self, ctx, member:discord.Member, *, message):
        if not message:
            embed = discord.Embed(title=f"Error", description=f"Please type in a message.", color=discord.Color.red())
            await ctx.reply(embed=embed)
            return
        try:
            await member.send(message)
            embed = discord.Embed(title="Success", description=f"Sent message to {member.mention}.", color=discord.Color.green())
            await ctx.reply(embed=embed)
        except discord.errors.Forbidden:
            embed = discord.Embed(title=f"Error", description=f"Could not send message to {member.mention}. They may have DMs disabled.", color=discord.Color.red())
            await ctx.reply(embed=embed)

    @commands.command()
    async def day(self, ctx, date: str = None):
        url = 'https://mbhs.edu/calendar/evenodd'
        try:
            response = requests.get(url)
            if response.status_code != 200:
                raise Exception("Failed to fetch the webpage.")
            if date:
                try:
                    dateObj = datetime.strptime(date, '%m/%d/%y')
                except ValueError:
                    embed = discord.Embed(title="Error", description=f"Invalid date. Use the format mm/dd/yy or enter a valid date.", color=discord.Color.red())
                    await ctx.reply(embed=embed)
                    return
            else:
                if datetime.now().hour >= 12:
                    dateObj = datetime.today().date() + timedelta(days=1)
                else:
                    dateObj = datetime.today()
            dateKey = dateObj.strftime('%a %b %d %Y')
            dateLoc = response.text.find(dateKey)
            if dateLoc == -1:
                embed = discord.Embed(title="Day", description=f"No school on {dateKey}.", color=discord.Color.green())
                await ctx.reply(embed=embed)
                return
            match = re.search(rf"{dateKey}\"\s*:\s*(\d)", response.text[dateLoc:])
            if match:
                oddeven = match.group(1)
                if oddeven == "1":
                    result = "an **ODD**"
                elif oddeven == "0":
                    result = "an **EVEN**"
                elif oddeven == "2":
                    result = "a no school"
                elif oddeven == "5":
                    embed = discord.Embed(title="Day", description=f"{dateKey} is weekend.", color=discord.Color.green())
                else:
                    result = "an unknown (error)"
                if oddeven != "5":
                    embed = discord.Embed(title="Day", description=f"{dateKey} is {result} day.", color=discord.Color.green())
            else:
                embed = discord.Embed(title="Error", description=f"Could not determine ODD/EVEN for{date}.", color=discord.Color.red())
        except Exception as e:
            embed = discord.Embed(title="Error", description=f"Could not fetch response from {url}.", color=discord.Color.red())
        await ctx.reply(embed=embed)

    @commands.command()
    async def die(self, ctx):
        if ctx.author.id == self.ownerID:
            embed = discord.Embed(title="Shutdown", description="Dying...dead", color=discord.Color.green())
            await ctx.reply(embed=embed)
            await self.bot.close()
        else:
            responses = [
                "no",
                "you too",
                "nah, i'd win",
                "dying...still alive",
                "dying...jk",
                "1v1 me",
                "the duck walked up to the lemonade stand",
                "its raining tacos from out of the sky",
                "living...alive"
            ]
            response = random.choice(responses)
            embed = discord.Embed(title=response, color=discord.Color.green())
            await ctx.reply(embed=embed)


async def setup(bot):
    await bot.add_cog(UtilitiesCog(bot))