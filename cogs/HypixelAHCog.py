import discord
from discord.ext import commands, tasks
import requests
import time
import json
import os
import aiohttp
import asyncio

cache_file = "cache/ah_cache.json"

class HypixelAHCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.hypixelAPIKey = os.getenv("hypixelAPIKeyBasic")
        self.channelID = 1185353211482222786
        self.trackedAuctions = {}

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
            if data.get("success") and data.get("player"):
                playerData = data["player"]
                specialPrefix = playerData.get("prefix")
                if specialPrefix != None:
                    return specialPrefix
                rank = playerData.get("rank")
                monthlySub = playerData.get("monthlyPackageRank")
                permRank = playerData.get("newPackageRank") or playerData.get("packageRank")
                if rank == "ADMIN":
                    return "[ADMIN]"
                elif rank == "MODERATOR":
                    return "[MOD]"
                elif rank == "HELPER":
                    return "[HELPER]"
                elif rank == "YOUTUBER":
                    return "[YOUTUBE]"
                elif monthlySub == "SUPERSTAR":
                    return "[MVP++]"
                elif permRank == "MVP_PLUS":
                    return "[MVP+]"
                elif permRank == "MVP":
                    return "[MVP]"
                elif permRank == "VIP_PLUS":
                    return "[VIP+]"
                elif permRank == "VIP":
                    return "[VIP]"
                else:
                    return "[Non]"
            else:
                return None
        else:
            return None

    def load_cache(self):
        try:
            with open(cache_file, "r") as file:
                ah_cache = json.load(file)
                if time.time() - ah_cache["timestamp"] < 600:
                    return ah_cache["data"]
        except (FileNotFoundError, json.JSONDecodeError, KeyError):
            return None
        return None
    
    def save_cache(self, data):
        data = {
            "timestamp": time.time(),
            "data": data
        }
        os.makedirs(os.path.dirname(cache_file), exist_ok=True)
        with open(cache_file, "w") as file:
            json.dump(data, file)

    async def get_auctions(self):
        page = 0
        allData = []
        async with aiohttp.ClientSession() as session:
            while True:
                async with session.get("https://api.hypixel.net/skyblock/auctions", params={"key": self.hypixelAPIKey, "page": page}) as response:
                    if response.status == 200:
                        ahData = await response.json()
                        allData.extend(ahData['auctions'])
                        page += 1
                        await asyncio.sleep(1)
                        if page >= ahData['totalPages']:
                            break
                    else:
                        print("error getting auction data from hypixel")
                        return None
        await asyncio.to_thread(self.save_cache, allData)
        return allData

    @commands.command(aliases=['ah'])
    async def auctions(self, ctx, ign: str):
        auctions = {}
        uuid, username = self.get_uuid(ign)
        rank = self.get_rank(uuid)
        if uuid == None:
            embed = discord.Embed(title=f"Could not find UUID for {ign}", color=discord.Color.red())
            await ctx.reply(embed=embed)
            return
        
        ahData = self.load_cache()
        if ahData == None:
            ahData = await self.get_auctions()
            if ahData == None:
                embed = discord.Embed(title=f"Could not get auction data from Hypixel", color=discord.Color.red())
                await ctx.reply(embed=embed)
                return
            
        count = 0
        if uuid not in auctions:
            auctions[uuid] = []
            for item in ahData:
                if item['auctioneer'] == uuid:
                    iteminfo = {}
                    iteminfo['name'] = item['item_name']
                    iteminfo['price'] = item['starting_bid']
                    if item['bin']:
                        iteminfo['type'] = "Bin"
                        remainingTime = (item['end'] - int(time.time() * 1000)) // 1000
                        iteminfo['time'] = remainingTime
                    else:
                        iteminfo['type'] = "Auction"
                    count += 1
                    auctions[uuid].append(iteminfo)

        embed = discord.Embed(title=f"Auctions for {rank} {username} ({count}/17)",color=discord.Color.green())
        if len(auctions[uuid]) == 0:
            embed.color = discord.Color.red()
            embed.add_field(name="No auctions found", value=f"{rank} {username} currently has no auctions set up", inline=False)
        else:
            for item in auctions[uuid]:
                embed.add_field(
                    name=item['name'], 
                    value=f"Price: `{{:,}}`.format(item['price'])`\nTime Left: `{item['time'] // 3600}h {(item['time'] % 3600) // 60}m {item['time'] % 60}s`\nType: `{item['type']}`", 
                    inline=False
                )
        await ctx.reply(embed=embed)

async def setup(bot):
    await bot.add_cog(HypixelAHCog(bot))

