from __future__ import annotations
from discord import app_commands
from discord.ext import commands
import discord


class Utility(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot


    @commands.hybrid_command(aliases=['link'])
    async def invite(self, ctx: commands.Context):
        """Invite the bot to your server"""
        perms = discord.Permissions.none()
        perms.administrator = True
        await ctx.send(f'<{discord.utils.oauth_url(self.bot.CLIENT_ID, permissions=perms)}>')

    @commands.hybrid_command()
    @commands.has_permissions(manage_messages=True)
    async def delete(self, ctx: commands.Context, amount: int = 1):
        """Deletes a specified amount of messages"""
        await ctx.defer()
        await ctx.channel.purge(limit=amount + 1)



    @commands.hybrid_command()
    async def ping(self, ctx: commands.Context):
        """Pong!"""
        await ctx.send(f'Pong! {round(self.bot.latency * 1000)}ms')

    
     


async def setup(bot: commands.Bot):
    await bot.add_cog(Utility(bot))
    
    