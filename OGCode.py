import random
import discord
from discord.ext import commands, tasks
from discord.utils import get
from discord.ext.commands import has_guild_permissions
import requests
import datetime
import os
from dotenv import load_dotenv

load_dotenv()
channelID = 1185353211482222786
myDiscordID = 535893497388204047
hypixelAPIKey = str(os.getenv('hypixelAPIKeyBasic'))
botToken = str(os.getenv('botToken'))

bot = commands.Bot(command_prefix="-", intents = discord.Intents.all())

censored_users = []
tracked_players = {}
auto_tracked_players = {'lceing'}

def get_uuid(ign):
    url = f"https://api.mojang.com/users/profiles/minecraft/{ign}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data['id']
    return None

def get_status(uuid):
    url = f"https://api.hypixel.net/status?key={hypixelAPIKey}&uuid={uuid}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if data.get('success') and data.get('session'):
            return data['session']['online'], data['session'].get('gameType')
    return None, None

@tasks.loop(seconds=10)
async def check_logins():
    for uuid, info in tracked_players.items():
        current_status, game_type = get_status(uuid)
        channel = bot.get_channel(info['channel_id'])
        if current_status is not None and current_status != info['online']:
            tracked_players[uuid]['online'] = current_status
            if current_status:
                tracked_players[uuid]['loginTime'] = datetime.datetime.now()
                embed = discord.Embed(title=f"{info['name']} has logged on to {game_type}", color=discord.Color.green())
                await channel.send(embed=embed)
            else:
                logoutTime = datetime.datetime.now()
                playtime = logoutTime - tracked_players[uuid]['loginTime']
                playtime_total_seconds = playtime.total_seconds()
                playtime_hours = int(playtime_total_seconds // 3600)
                playtime_minutes = int((playtime_total_seconds % 3600) // 60)
                playtime_seconds = int(playtime_total_seconds - playtime_hours * 3600 - playtime_minutes * 60)
                embed = discord.Embed(title = f"Log off", description = f"{author.mention} {info['name']} has logged off.\nSession playtime: {playtime_hours} hours, {playtime_minutes} minutes, {playtime_seconds} seconds",color=discord.Color.red())
                await channel.send(embed=embed)
        if game_type is not None and game_type != info['gamemode'] and info['gamemode'] != None:
            tracked_players[uuid]['gamemode'] = game_type
            embed = discord.Embed(title=f"{info['name']} has switched gamemodes to {game_type}", color=discord.Color.blue())
            await channel.send(embed=embed)

@bot.event
async def on_ready():
    global author
    author = bot.get_user(myDiscordID)
    print("Frostfall is online")
    await auto_track_players()
    check_logins.start()

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, discord.ext.commands.errors.CommandNotFound):
        embed = discord.Embed(title="You probably typed something wrong or that command doesn't exist", color=discord.Color.blue())
        await ctx.reply(embed=embed)

@bot.event
async def on_message(message):
    await bot.process_commands(message)
    if message.author == bot.user:
        return
    if message.author.id in censored_users:
        await message.delete()

@bot.command()
async def ping(ctx):
    embed = discord.Embed(title=f"Pong! Latency: {round(bot.latency * 1000)}ms", color=discord.Color.blue())
    await ctx.reply(embed=embed)

@bot.command(aliases=['8ball'])
async def eightball(ctx, *, question):
    responses = ["No lol", "Jason sucks at coding, try again later", "Not happening", "Yeah sure.", "Get your serve in first before asking me", "Why u ask me", "Probably...", "idk, i dont have the imagination to think of more responses, help me out.", "It is certain", "It is decidedly so", "Without a doubt", "Yes definitely", "My reply is no", "Outlook not so good", "Don’t count on it", "As I see it, yes", "Outlook good", "Signs point to yes"]
    embed = discord.Embed(title=f"**Question: ** {question}\n**Answer: ** {random.choice(responses)}", color=discord.Color.blue())
    await ctx.reply(embed=embed)

role_id = 1206438975028330566
@bot.command()
@has_guild_permissions(mute_members=True)
async def mute(ctx, member:discord.Member):
    role = discord.utils.get(ctx.guild.roles, get(guild.roles, id = role_id))
    if role in member.roles:
        embed = discord.Embed(title="Already Muted", description = f"{member.mention} has already been muted", color=discord.Color.red())
        await ctx.reply(embed=embed)
    elif role not in member.roles:
        guild = ctx.guild
        await member.add_roles(role)
        embed = discord.Embed(title="Muted", description = f"{member.mention} was muted, L", color=discord.Color.red())
        await ctx.reply(embed=embed)
    else:
        embed = discord.Embed(title="Can't mute a bot lmfao", color=discord.Color.red())
        await ctx.reply(embed=embed)
        
@mute.error
async def mute_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        embed = discord.Embed(title="No Perms >:D", color=discord.Color.blue())
        await ctx.reply(embed=embed)
    elif isinstance(error, commands.MissingRequiredArgument):
        embed = discord.Embed(title="You idiot you typed the command wrong", color=discord.Color.blue())
        await ctx.reply(embed=embed)
    elif isinstance(error, commands.BadArgument):
        embed = discord.Embed(title="You idiot you typed the command wrong", color=discord.Color.blue())
        await ctx.reply(embed=embed)
    elif isinstance(error, commands.CommandInvokeError):
        embed = discord.Embed(title="You idiot you typed the command wrong", color=discord.Color.blue())
        await ctx.reply(embed=embed)
    elif isinstance(error, commands.TooManyArguments):
        embed = discord.Embed(title="You idiot you typed the command wrong", color=discord.Color.blue())
        await ctx.reply(embed=embed)
    elif isinstance(error, commands.CheckFailure):
        embed = discord.Embed(title="You idiot you typed the command wrong", color=discord.Color.blue())
        await ctx.reply(embed=embed)
    else:
        await ctx.reply("something went wrong somehow go spam jason")

@bot.command()
async def unmute(ctx, member:discord.Member):
    role = discord.utils.get(ctx.guild.roles, name = "Muted")
    if role not in member.roles:
        embed = discord.Embed(title="Already Unmuted", description = f"{member.mention} has already been unmuted", color=discord.Color.red())
        await ctx.reply(embed=embed)
    else:
        guild = ctx.guild
        await member.remove_roles(role)
        embed = discord.Embed(title="Unmuted", description = f"{member.mention} was unmuted, W", color=discord.Color.green())
        await ctx.reply(embed=embed)

@bot.command()
async def die(ctx):
    await ctx.reply("dying...dead")
    await bot.close()

@die.error
async def die_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        embed = discord.Embed(title="No Perms >:D", color=discord.Color.blue())
        await ctx.reply(embed=embed)
    elif isinstance(error, commands.MissingRequiredArgument):
        embed = discord.Embed(title="You idiot you typed the command wrong", color=discord.Color.blue())
        await ctx.reply(embed=embed)
    elif isinstance(error, commands.BadArgument):
        embed = discord.Embed(title="You idiot you typed the command wrong", color=discord.Color.blue())
        await ctx.reply(embed=embed)
    elif isinstance(error, commands.CommandInvokeError):
        embed = discord.Embed(title="You idiot you typed the command wrong", color=discord.Color.blue())
        await ctx.reply(embed=embed)
    elif isinstance(error, commands.TooManyArguments):
        embed = discord.Embed(title="You idiot you typed the command wrong", color=discord.Color.blue())
        await ctx.reply(embed=embed)
    elif isinstance(error, commands.CheckFailure):
        embed = discord.Embed(title="You idiot you typed the command wrong", color=discord.Color.blue())
        await ctx.reply(embed=embed)
    else:
        await ctx.reply("something went wrong somehow go spam jason")

@bot.command()
@has_guild_permissions(mute_members=True)
async def censor(ctx, member: discord.Member):
    if member.id == ctx.author.id or member.id in censored_users:
        return
    censored_users.append(member.id)
    embed = discord.Embed(title=f"{member.display_name} has been censored", color=discord.Color.red())
    await ctx.send(embed=embed)

@censor.error
async def censor_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        embed = discord.Embed(title="No Perms >:D", color=discord.Color.blue())
        await ctx.reply(embed=embed)
    elif isinstance(error, commands.MissingRequiredArgument):
        embed = discord.Embed(title="You idiot you typed the command wrong", color=discord.Color.blue())
        await ctx.reply(embed=embed)
    elif isinstance(error, commands.BadArgument):
        embed = discord.Embed(title="You idiot you typed the command wrong", color=discord.Color.blue())
        await ctx.reply(embed=embed)
    elif isinstance(error, commands.CommandInvokeError):
        embed = discord.Embed(title="You idiot you typed the command wrong", color=discord.Color.blue())
        await ctx.reply(embed=embed)
    elif isinstance(error, commands.TooManyArguments):
        embed = discord.Embed(title="You idiot you typed the command wrong", color=discord.Color.blue())
        await ctx.reply(embed=embed)
    elif isinstance(error, commands.CheckFailure):
        embed = discord.Embed(title="You idiot you typed the command wrong", color=discord.Color.blue())
        await ctx.reply(embed=embed)
    else:
        await ctx.reply("something went wrong somehow go spam jason")

@bot.command()
async def uncensor(ctx, member: discord.Member):
    if member.id == ctx.author.id or member.id not in censored_users:
        return
    censored_users.remove(member.id)
    embed = discord.Embed(title=f"{member.display_name} has been uncensored", color=discord.Color.green())
    await ctx.send(embed=embed)

@bot.command()
async def clear(ctx, amount = 0):
    await ctx.channel.purge(limit = amount+1)

@bot.command()
async def track(ctx, ign: str):
    uuid = get_uuid(ign)
    if uuid:
        if uuid not in tracked_players:
            online_status, game_type = get_status(uuid)
            if online_status is not None:
                tracked_players[uuid] = {'name': ign, 'online': online_status, 'gamemode': game_type, 'channel_id': ctx.channel.id}
                if online_status:
                    tracked_players[uuid]['loginTime'] = datetime.datetime.now()
                    embed = discord.Embed(title=f"Started tracking {ign}.\nCurrent status: Online\nIn gamemode: {game_type}", color=discord.Color.green())
                else:
                    embed = discord.Embed(title=f"Started tracking {ign}.\nCurrent status: Offline", color=discord.Color.green())
                await ctx.reply(embed=embed)
            else:
                embed = discord.Embed(title=f"Could not retrieve status for {ign}", color=discord.Color.red())
                await ctx.reply(embed=embed)
        else:
            embed = discord.Embed(title=f"Already tracking {ign}", color=discord.Color.blue())
            await ctx.reply(embed=embed)
    else:
        embed = discord.Embed(title=f"Could not find UUID for {ign}", color=discord.Color.red())
        await ctx.reply(embed=embed)

@bot.command()
async def untrack(ctx, ign: str):
    uuid = get_uuid(ign)
    if uuid and uuid in tracked_players:
        del tracked_players[uuid]
        embed = discord.Embed(title=f"Stopped tracking {ign}", color=discord.Color.blue())
        await ctx.reply(embed=embed)
    else:
        embed = discord.Embed(title=f"Not tracking {ign}", color=discord.Color.blue())
        await ctx.reply(embed=embed)

async def auto_track_players():
    channel = bot.get_channel(channelID)
    for player in auto_tracked_players:
        uuid = get_uuid(player)
        if uuid and uuid not in tracked_players:
            online_status, game_type = get_status(uuid)
            if online_status is not None:
                tracked_players[uuid] = {'name': player, 'online': online_status, 'gamemode': game_type, 'channel_id': channelID}
                if online_status:
                    tracked_players[uuid]['loginTime'] = datetime.datetime.now()
                    embed = discord.Embed(title=f"Automatically started tracking {player}.\nCurrent status: Online\nIn gamemode: {game_type}", color=discord.Color.green())
                else:
                    embed = discord.Embed(title=f"Automatically started tracking {player}.\nCurrent status: Offline", color=discord.Color.green())
                await channel.send(embed=embed)

bot.run(botToken)