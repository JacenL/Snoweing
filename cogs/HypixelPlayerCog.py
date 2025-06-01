import discord
from discord.ext import commands, tasks
import requests
import datetime
import os
import re

class HypixelPlayerCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.trackedPlayers = {}
        self.autoTrackedPlayers = {"lceing"}
        self.dailyPlaytime = {}
        self.hypixelAPIKey = os.getenv("hypixelAPIKeyDev")
        self.channelID = 1185353211482222786
        self.author = bot.get_user(535893497388204047)
        self.check_logins.start()

    def get_uuid(self, ign):
        url = f"https://api.mojang.com/users/profiles/minecraft/{ign}"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            return data['id'], data['name']
        return None, None
    
    def get_rank(self, uuid):
        response = requests.get(f"https://api.hypixel.net/player?key={self.hypixelAPIKey}&uuid={uuid}")
        if response.status_code == 200:
            data = response.json()
            boringPrefixes = {"[ADMIN]", "[MOD]", "[HELPER]", "[YOUTUBE]", "[OWNER]"}
            if data.get("success") and data.get("player"):
                if data["player"].get("prefix") not in boringPrefixes and data["player"].get("prefix"):
                    if re.sub(r"[^A-Z+\-\[\]0-9]", "",data["player"].get("prefix")) in (["[PIG+++]", "[INNIT]"]):
                        return re.sub(r"[^A-Z+\-\[\]0-9]", "",data["player"].get("prefix")), int("FF69B4", 16)
                    elif re.sub(r"§[0-9A-FK-OR]|[^A-Z+\-\[\]0-9]", "",data["player"].get("prefix")) in (["[EVENTS]", "[MOJANG]"]):
                        return re.sub(r"§[0-9A-FK-OR]|[^A-Z+\-\[\]0-9]", "",data["player"].get("prefix")), int("FFD700", 16)
                    else:
                        return re.sub(r"§[0-9A-FK-OR]|[^A-Z+\-\[\]0-9]", "",data["player"].get("prefix")), int("FF0000", 16)
                rank = data["player"].get("rank")
                monthlySub = data["player"].get("monthlyPackageRank")
                permRank = data["player"].get("newPackageRank") or data["player"].get("packageRank")
                if rank == "ADMIN":
                    return "[ADMIN]", int("AA0000", 16)
                elif rank == "MODERATOR":
                    return "[MOD]", int("00AA00", 16)
                elif rank == "HELPER":
                    return "[HELPER]", int("5555FF", 16)
                elif rank == "YOUTUBER":
                    return "[YOUTUBE]", int("FF5555", 16)
                elif monthlySub == "SUPERSTAR":
                    return "[MVP++]", int("FFAA00", 16)
                elif permRank == "MVP_PLUS":
                    return "[MVP+]", int("55FFFF", 16)
                elif permRank == "MVP":
                    return "[MVP]", int("55FFFF", 16)
                elif permRank == "VIP_PLUS":
                    return "[VIP+]", int("55FF55", 16)
                elif permRank == "VIP":
                    return "[VIP]", int("55FF55", 16)
                else:
                    return "[Non]", int("AAAAAA", 16)
            else:
                return None, None
        else:
            return None, None
        
    def get_status(self, uuid):
        url = f"https://api.hypixel.net/status?key={self.hypixelAPIKey}&uuid={uuid}"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            if data.get('success') and data.get('session'):
                return data['session']['online'], data['session'].get('gameType')
        return None, None

    @tasks.loop(seconds=5)
    async def check_logins(self):
        for uuid, info in self.trackedPlayers.items():
            current_status, game_type = self.get_status(uuid)
            channel = self.bot.get_channel(info['channel_id'])
            if current_status is not None and current_status != info['online']:
                self.trackedPlayers[uuid]['online'] = current_status
                if current_status:
                    if uuid not in self.dailyPlaytime:
                        self.dailyPlaytime[uuid] = {'currentDay': datetime.date.today(), 'currentPlaytime': 0}
                    if uuid in self.dailyPlaytime:
                        self.dailyPlaytime[uuid]['currentDay'] = datetime.date.today()
                    self.trackedPlayers[uuid]['loginTime'] = datetime.datetime.now()
                    embed = discord.Embed(title=f"{info['rank']} {info['name']} has logged on to {game_type}", color=discord.Color.green())
                    await channel.send(embed=embed)
                else:
                    logoutTime = datetime.datetime.now()
                    playtime = logoutTime - self.trackedPlayers[uuid]['loginTime']
                    playtime_total_seconds = playtime.total_seconds()
                    if uuid in self.dailyPlaytime:
                        self.dailyPlaytime[uuid]['currentPlaytime'] += playtime_total_seconds
                    playtime_hours = int(playtime_total_seconds // 3600)
                    playtime_minutes = int((playtime_total_seconds % 3600) // 60)
                    playtime_seconds = int(playtime_total_seconds - playtime_hours * 3600 - playtime_minutes * 60)
                    embed = discord.Embed(title = f"Log off", description = f"{self.author.mention} {info['rank']} {info['name']} has logged off.\nSession playtime: {playtime_hours} hours, {playtime_minutes} minutes, {playtime_seconds} seconds",color=discord.Color.red())
                    await channel.send(embed=embed)
            if game_type is not None and game_type != info['gamemode'] and info['gamemode'] != None:
                self.trackedPlayers[uuid]['gamemode'] = game_type
                embed = discord.Embed(title=f"{info['rank']} {info['name']} has switched gamemodes to {game_type}", color=discord.Color.blue())
                await channel.send(embed=embed)
        for uuid in self.dailyPlaytime:
            if self.dailyPlaytime[uuid]['currentDay'] != datetime.date.today():
                total_seconds = self.dailyPlaytime[uuid]['currentPlaytime']
                hours = int(total_seconds // 3600)
                minutes = int((total_seconds % 3600) // 60)
                seconds = int(total_seconds % 60)
                embed = discord.Embed(title=f"Total playtime for {self.trackedPlayers[uuid]['name']} today", description=f"{hours} hours, {minutes} minutes, {seconds} seconds", color=discord.Color.blue())
                await channel.send(embed=embed)
                self.dailyPlaytime[uuid]['currentPlaytime'] = 0
                self.dailyPlaytime[uuid]['currentDay'] = datetime.date.today()

    @commands.command()
    async def track(self, ctx, ign: str):
        uuid, username = self.get_uuid(ign)
        rank, hexColor = self.get_rank(uuid)
        if uuid:
            if uuid not in self.trackedPlayers:
                online_status, game_type = self.get_status(uuid)
                if online_status is not None:
                    self.trackedPlayers[uuid] = {'name': username, 'rank': rank, 'online': online_status, 'gamemode': game_type, 'channel_id': ctx.channel.id}
                    if online_status:
                        self.trackedPlayers[uuid]['loginTime'] = datetime.datetime.now()
                        embed = discord.Embed(title=f"Started tracking {rank} {username}.\nCurrent status: Online\nIn gamemode: {game_type}", color=discord.Color.green())
                    else:
                        embed = discord.Embed(title=f"Started tracking {rank} {username}.\nCurrent status: Offline", color=discord.Color.green())
                    await ctx.reply(embed=embed)
                else:
                    embed = discord.Embed(title=f"Could not retrieve status for {username}", color=discord.Color.red())
                    await ctx.reply(embed=embed)
            else:
                embed = discord.Embed(title=f"Already tracking {rank} {username}", color=discord.Color.blue())
                await ctx.reply(embed=embed)
        else:
            embed = discord.Embed(title=f"Could not find UUID for {username}", color=discord.Color.red())
            await ctx.reply(embed=embed)

    @commands.command()
    async def untrack(self, ctx, ign: str):
        uuid, username = self.get_uuid(ign)
        rank, hexColor = self.get_rank(uuid)
        if uuid and uuid in self.trackedPlayers:
            del self.trackedPlayers[uuid]
            self.dailyPlaytime.pop(uuid, None)
            embed = discord.Embed(title=f"Stopped tracking {rank} {username}", color=discord.Color.blue())
            await ctx.reply(embed=embed)
        else:
            embed = discord.Embed(title=f"Not tracking {rank} {username}", color=discord.Color.blue())
            await ctx.reply(embed=embed)

    @check_logins.before_loop
    async def before_check_logins(self):
        await self.bot.wait_until_ready()
        await self.auto_track_players()

    async def auto_track_players(self):
        channel = self.bot.get_channel(self.channelID)
        for player in self.autoTrackedPlayers:
            uuid, username = self.get_uuid(player)
            rank, hexColor = self.get_rank(uuid)
            if uuid and uuid not in self.trackedPlayers:
                online_status, game_type = self.get_status(uuid)
                if online_status is not None:
                    self.trackedPlayers[uuid] = {'name': username, 'rank': rank,'online': online_status, 'gamemode': game_type, 'channel_id': self.channelID}
                    if online_status:
                        self.trackedPlayers[uuid]['loginTime'] = datetime.datetime.now()
                        embed = discord.Embed(title=f"Automatically started tracking {rank} {username}.\nCurrent status: Online\nIn gamemode: {game_type}", color=discord.Color.green())
                    else:
                        embed = discord.Embed(title=f"Automatically started tracking {rank} {username}.\nCurrent status: Offline", color=discord.Color.green())
                    await channel.send(embed=embed)

    @commands.command(aliases=['pt'])
    async def playtime(self, ctx, ign: str):
        uuid, username = self.get_uuid(ign)
        rank, hexColor = self.get_rank(uuid)
        if uuid in self.dailyPlaytime and self.dailyPlaytime[uuid]['currentDay'] == datetime.date.today():
            total_seconds = self.dailyPlaytime[uuid]['currentPlaytime']
            hours = int(total_seconds // 3600)
            minutes = int((total_seconds % 3600) // 60)
            seconds = int(total_seconds % 60)
            embed = discord.Embed(title=f"Playtime for {rank} {username} Today", description=f"{hours} hours, {minutes} minutes, {seconds} seconds", color=discord.Color.blue())
            await ctx.reply(embed=embed)
        elif username == None:
            embed = discord.Embed(title=f"Hypixel API Cooldown", description="Try again in a few seconds", color=discord.Color.blue())
            await ctx.reply(embed=embed)
        else:
            embed = discord.Embed(title=f"No tracked playtime for {rank} {username}", color=discord.Color.blue())
            await ctx.reply(embed=embed)

    @commands.command()
    async def rank(self, ctx, ign: str):
        uuid, username = self.get_uuid(ign)
        rank, hexColor = self.get_rank(uuid)
        if uuid:
            embed = discord.Embed(title=f"{rank} {username}", color=hexColor)
            await ctx.reply(embed=embed)
        else:
            embed = discord.Embed(title=f"Could not find UUID for {ign}", color=hexColor)
            await ctx.reply(embed=embed)

async def setup(bot):
    await bot.add_cog(HypixelPlayerCog(bot))
