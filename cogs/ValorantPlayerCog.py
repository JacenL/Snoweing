import discord
from discord.ext import commands, tasks
import requests
import requests
import os

class ValorantPlayerCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.apiKey = os.getenv("valorantAPIKey")
        self.channelID = 1185353211482222786
        self.checker.start()
        self.trackedPlayers = {}

    def get_status(self, user, tag):
        response = requests.get(
            f"https://api.henrikdev.xyz/valorant/v3/matches/na/{user}/{tag}",
            headers={"Authorization":f"{self.apiKey}","Accept":"*/*"},
        )
        data = response.json()
        matches = data["data"]
        match = matches[0]
        map = match["metadata"]["map"]
        mode = match["metadata"]["mode"]
        duration = match["metadata"]["game_length"]

        for player in match["players"]["all_players"]:
            if player["name"] == user and player["tag"] == tag:
                pt = player["session_playtime"]["milliseconds"]
                # minutes=int((pt_ms/(1000*60))%60)
                # seconds=int((pt_ms/1000)%60)
                team = player["team"]
                kills = player["stats"]["kills"]
                deaths = player["stats"]["deaths"]
                assists = player["stats"]["assists"]
                score = player["stats"]["score"]
                headshots = player["stats"]["headshots"]
                bodyshots = player["stats"]["bodyshots"]
                legshots = player["stats"]["legshots"]

                rounds = match["metadata"].get("rounds_played", 0)
                if rounds != 0:
                    acs = player["stats"]["score"] / rounds

                team = player.get("team")
                teams = match["teams"]
                result = None
                if team == "Red":
                    result = teams["Red"]["has_won"]
                elif team == "Blue":
                    result = teams["Blue"]["has_won"]
                else:
                    result = None


        
        


    @tasks.loop(seconds=15)
    async def checker (self):
        for id in self.trackedPlayers:
            index = id.find("#")
            username = id[:index]
            tag = id[index + 1:]

            
            if data != self.trackedPlayers[id]["lastData"]:
                channel = self.bot.get_channel(self.channelID)
                await channel.send(f"New match data for {username}#{tag}: {data}")
                self.trackedPlayers[id]["lastData"] = data

    @commands.command()
    async def val(self, ctx, userid: str):

        response = requests.get(
            f"https://api.henrikdev.xyz/valorant/v3/matches/na/{username}/{tag}",
            headers={"Authorization":"HDEV-4d30ba7e-2a11-4960-8f6d-777905f14589)","Accept":"*/*"},
        )
        data = response.json()
        await ctx.reply(f"{data}")

async def setup(bot):
    await bot.add_cog(ValorantPlayerCog(bot))