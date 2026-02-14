import discord
from discord.ext import commands
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import os
from dotenv import load_dotenv

load_dotenv()

sp = spotipy.Spotify(
    auth_manager=SpotifyClientCredentials(
        client_id=os.getenv("spotifyClientID"),
        client_secret=os.getenv("spotifyClientSecret")
    )
)

class SpotifyCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def searchPlaylist(self, playlistSearch):
        results = sp.search(
            q=playlistSearch,
            type='playlist',
            limit=50
        )

        playlists = results['playlists']['items']
        searchInput = playlistSearch.lower().split()
        matchingPlaylists = []

        for playlist in playlists:
            name = playlist['name'].lower()
            if all(word in name for word in searchInput):
                matchingPlaylists.append(playlist)

        return matchingPlaylists

    @commands.command()
    async def playlist(self, ctx, *, playlistName: str):
        try:
            playlists = self.searchPlaylist(playlistName)
            print(playlists)
            if playlists == []:
                embed = discord.Embed(title=f"**Error**", description=f"No playlists found with the name '{playlistName}'.", color=discord.Color.red())
                await ctx.reply(embed=embed)
                return
            embed = discord.Embed(
                title=f"Playlists matching '{playlistName}'",
                description="All based on spotify API search (only the most popular results show up):",
                color=discord.Color.green()
            )
            for i, playlist in enumerate(playlists[:10], start=1):
                name = playlist["name"]
                owner = playlist["owner"]["display_name"]
                url = playlist["external_urls"]["spotify"]

                embed.add_field(
                    name=f"{i}. {name}",
                    value=f"By: {owner}\n[Open in Spotify]({url})",
                    inline=False
                )
            await ctx.reply(embed=embed)
        except Exception as e:
            embed = discord.Embed(title=f"**Error**", description=f"Failed to search for playlists: {e}", color=discord.Color.red())

async def setup(bot):
    await bot.add_cog(SpotifyCog(bot))
