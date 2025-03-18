import discord
from discord.ext import commands

class ChannelCheckerCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.channelID = 1163434758047531069
        self.messagingChannelID = 1351404751316844604
        self.trackedAuctions = {}
    
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.channel.id == self.channelID and not message.author.bot:
            embed = discord.Embed(description=f"New message from AOT Codes Discord: {message.content}", color=discord.Color.blue())
            logChannel = self.bot.get_channel(self.messagingChannelID)
            await logChannel.send(embed=embed)


async def setup(bot):
    await bot.add_cog(ChannelCheckerCog(bot))