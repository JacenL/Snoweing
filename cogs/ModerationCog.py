import discord
from discord.ext import commands

class ModerationCog(commands.Cog):
    def __init__(self, bot):
        self.censored_users = []
        self.bot = bot

    @commands.command()
    @commands.has_guild_permissions(mute_members=True)
    async def mute(self, ctx, member:discord.Member):
        role = None
        for r in ctx.guild.roles:
            if r.name.lower() == "muted":
                role = r
                break
        if role in member.roles:
            embed = discord.Embed(title="Already Muted", description = f"{member.mention} has already been muted", color=discord.Color.red())
            await ctx.reply(embed=embed)
        elif role not in member.roles:
            await member.add_roles(role)
            embed = discord.Embed(title="Muted", description = f"{member.mention} was muted, L", color=discord.Color.red())
            await ctx.reply(embed=embed)
        else:
            embed = discord.Embed(title="Can't mute a bot lmfao", color=discord.Color.red())
            await ctx.reply(embed=embed)

    @mute.error
    async def mute_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            embed = discord.Embed(title="No Perms >:D", color=discord.Color.blue())
            await ctx.reply(embed=embed)
        else:
            embed = discord.Embed(title="You idiot you typed the command wrong", color=discord.Color.blue())
            await ctx.reply(embed=embed)

    @commands.command()
    async def unmute(self, ctx, member:discord.Member):
        role = discord.utils.get(ctx.guild.roles, name = "Muted")
        if role not in member.roles:
            embed = discord.Embed(title="Already Unmuted", description = f"{member.mention} has already been unmuted", color=discord.Color.red())
            await ctx.reply(embed=embed)
        else:
            await member.remove_roles(role)
            embed = discord.Embed(title="Unmuted", description = f"{member.mention} was unmuted, W", color=discord.Color.green())
            await ctx.reply(embed=embed)

    @commands.command()
    @commands.has_guild_permissions(mute_members=True)
    async def censor(self, ctx, member: discord.Member):
        if member.id == ctx.author.id or member.id in self.censored_users:
            return
        self.censored_users.append(member.id)
        embed = discord.Embed(title=f"{member.display_name} has been censored", color=discord.Color.red())
        await ctx.reply(embed=embed)

    @censor.error
    async def censor_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            embed = discord.Embed(title="No Perms >:D", color=discord.Color.blue())
            await ctx.reply(embed=embed)
        else:
            embed = discord.Embed(title="You idiot you typed the command wrong", color=discord.Color.blue())
            await ctx.reply(embed=embed)

    @commands.command()
    async def uncensor(self, ctx, member: discord.Member):
        if member.id == ctx.author.id or member.id not in self.censored_users:
            return
        self.censored_users.remove(member.id)
        embed = discord.Embed(title=f"{member.display_name} has been uncensored", color=discord.Color.green())
        await ctx.reply(embed=embed)
    
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return
        if message.author.id in self.censored_users:
            await message.delete()

async def setup(bot):
    await bot.add_cog(ModerationCog(bot))
