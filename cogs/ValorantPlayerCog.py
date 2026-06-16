import os
import discord
import httpx
from discord.ext import commands, tasks

class ValorantPlayerCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.apiKey = os.getenv("valorantAPIKey")
        if not self.apiKey:
            print("WARNING: 'valorantAPIKey' environment variable not found.")
            
        self.channelID = 1185353211482222786
        self.trackedPlayers = {}
        self.checker.start()

    def cog_unload(self):
        self.checker.cancel()

    async def get_status(self, user: str, tag: str):
        headers = {
            "Authorization": self.apiKey,
            "Accept": "*/*"
        }

        async with httpx.AsyncClient() as client:
            # fetch match data
            try:
                response = await client.get(
                    f"https://api.henrikdev.xyz/valorant/v3/matches/na/{user}/{tag}",
                    headers=headers
                )
                if response.status_code != 200:
                    return None
                data = response.json()
            except Exception:
                return None

            # fetch rank data
            rank = "Unranked"
            try:
                mmr_response = await client.get(
                    f"https://api.henrikdev.xyz/valorant/v2/mmr/na/{user}/{tag}",
                    headers=headers
                )
                if mmr_response.status_code == 200:
                    mmr_data = mmr_response.json()
                    tier = mmr_data.get("data", {}).get("current_data", {}).get("currenttierpatched")
                    if tier:
                        rank = tier
            except Exception:
                pass

        matches = data.get("data", [])
        if not matches:
            return None
            
        match = matches[0]
        match_id = match["metadata"]["matchid"]
        game_map = match["metadata"]["map"]
        mode = match["metadata"]["mode"]
        duration = match["metadata"]["game_length"]

        pt = kills = deaths = assists = headshots = bodyshots = legshots = 0
        acs = 0.0
        team = "Unknown"
        
        for player in match["players"]["all_players"]:
            if player["name"].lower() == user.lower() and player["tag"].lower() == tag.lower():
                pt = player.get("session_playtime", {}).get("milliseconds", 0)
                stats = player["stats"]
                kills = stats["kills"]
                deaths = stats["deaths"]
                assists = stats["assists"]
                headshots = stats["headshots"]
                bodyshots = stats["bodyshots"]
                legshots = stats["legshots"]

                rounds = match["metadata"].get("rounds_played", 0)
                if rounds > 0:
                    acs = stats["score"] / rounds

                team = player["team"].capitalize()
                break

        teams = match["teams"]
        result = "Unknown"
        score = "N/A"
        
        if team in teams and teams[team] is not None:
            won = teams[team]["has_won"]
            result = "Victory" if won else "Defeat"
            other_team = "Blue" if team == "Red" else "Red"
            score = f"{teams[team]['rounds_won']} - {teams[other_team]['rounds_won']}"

        return {
            "match_id": match_id,
            "map": game_map,
            "mode": mode,
            "duration": duration,
            "playtime_ms": pt,
            "kills": kills,
            "deaths": deaths,
            "assists": assists,
            "acs": round(acs, 1),
            "score": score,
            "result": result,
            "headshots": headshots,
            "bodyshots": bodyshots,
            "legshots": legshots,
            "rank": rank
        }

    @tasks.loop(seconds=15)
    async def checker(self):
        await self.bot.wait_until_ready()
        channel = self.bot.get_channel(self.channelID)
        if not channel:
            return

        for player_id in list(self.trackedPlayers.keys()):
            if "#" not in player_id:
                continue
                
            username, tag = player_id.split("#", 1)
            player_info = await self.get_status(username, tag)
            
            if not player_info:
                continue

            current_match_id = player_info["match_id"]
            last_match_id = self.trackedPlayers[player_id].get("lastMatchId")

            if last_match_id is None:
                self.trackedPlayers[player_id]["lastMatchId"] = current_match_id
                continue

            if current_match_id != last_match_id:
                self.trackedPlayers[player_id]["lastMatchId"] = current_match_id
                
                playtime_ms = player_info["playtime_ms"]
                total_seconds = int(playtime_ms / 1000)
                minutes = total_seconds // 60
                seconds = total_seconds % 60
                duration_str = f"{minutes}m {seconds}s"

                color = discord.Color.green() if player_info["result"] == "Victory" else discord.Color.red()
                embed = discord.Embed(
                    title=f"Match Completed: {username}#{tag}",
                    description=f"Result: {player_info['result']} ({player_info['score']})",
                    color=color
                )
                embed.add_field(name="Rank", value=player_info["rank"], inline=True)
                embed.add_field(name="Map / Mode", value=f"{player_info['map']} ({player_info['mode']})", inline=True)
                embed.add_field(name="Match Playtime", value=duration_str, inline=True)
                embed.add_field(name="K / D / A", value=f"{player_info['kills']} / {player_info['deaths']} / {player_info['assists']}", inline=True)
                embed.add_field(name="ACS", value=str(player_info['acs']), inline=True)
                embed.add_field(name="HS / Body / Leg", value=f"{player_info['headshots']} / {player_info['bodyshots']} / {player_info['legshots']}", inline=True)
                
                await channel.send(embed=embed)

    @commands.command(name="val")
    async def val(self, ctx, *, userid: str):
        if "#" not in userid:
            embed = discord.Embed(
                title="Invalid Format",
                description="Please provide your Riot ID formatted with a hashtag. Example: Username#NA1",
                color=discord.Color.red()
            )
            await ctx.reply(embed=embed)
            return

        username, tag = userid.split("#", 1)
        await ctx.typing()
        
        player_info = await self.get_status(username, tag)
        if not player_info:
            embed = discord.Embed(
                title="Data Retrieval Error",
                description="Could not retrieve match data for that player. Verify ID or API availability.",
                color=discord.Color.red()
            )
            await ctx.reply(embed=embed)
            return

        color = discord.Color.green() if player_info["result"] == "Victory" else discord.Color.red()
        embed = discord.Embed(
            title=f"Recent Match: {username}#{tag}",
            description=f"Result: {player_info['result']} ({player_info['score']})",
            color=color
        )
        embed.add_field(name="Rank", value=player_info["rank"], inline=True)
        embed.add_field(name="Map / Mode", value=f"{player_info['map']} ({player_info['mode']})", inline=True)
        embed.add_field(name="K / D / A", value=f"{player_info['kills']} / {player_info['deaths']} / {player_info['assists']}", inline=True)
        embed.add_field(name="ACS", value=str(player_info['acs']), inline=True)
        
        await ctx.reply(embed=embed)

    @commands.command(name="valtrack")
    async def valtrack(self, ctx, *, userid: str):
        if "#" not in userid:
            embed = discord.Embed(
                title="Invalid Format",
                description="Use Name#TAG format to begin tracking.",
                color=discord.Color.red()
            )
            await ctx.reply(embed=embed)
            return
            
        if userid in self.trackedPlayers:
            embed = discord.Embed(
                title="Tracking Warning",
                description="This player profile is already being tracked.",
                color=discord.Color.orange()
            )
            await ctx.reply(embed=embed)
            return
            
        self.trackedPlayers[userid] = {"lastMatchId": None}
        embed = discord.Embed(
            title="Tracking Confirmed",
            description=f"Now actively tracking match cycles for: {userid}",
            color=discord.Color.green()
        )
        await ctx.reply(embed=embed)

    @commands.command(name="valuntrack")
    async def valuntrack(self, ctx, *, userid: str):
        if "#" not in userid:
            embed = discord.Embed(
                title="Invalid Format",
                description="Use Name#TAG format to untrack a player.",
                color=discord.Color.red()
            )
            await ctx.reply(embed=embed)
            return

        if userid not in self.trackedPlayers:
            embed = discord.Embed(
                title="Not Found",
                description=f"{userid} is not currently being tracked.",
                color=discord.Color.orange()
            )
            await ctx.reply(embed=embed)
            return

        del self.trackedPlayers[userid]
        embed = discord.Embed(
            title="Tracking Removed",
            description=f"No longer tracking {userid}.",
            color=discord.Color.green()
        )
        await ctx.reply(embed=embed)

async def setup(bot):
    await bot.add_cog(ValorantPlayerCog(bot))