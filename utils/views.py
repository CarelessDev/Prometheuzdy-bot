from __future__ import annotations
from main import Oppy
import discord
import asyncio
from discord.ext import commands

from .promptpay import PromptPay
from .embeds import user_embed


class Show_User_Dropdown(discord.ui.Select):
    def __init__(self, bot: 'Oppy', view: Show_User_View, all_users: dict, ephemeral: bool):
        self._view = view
        self.bot = bot
        self.ctx = self.view.ctx
        self.ephemeral = ephemeral
        # dropdown menus
        # using guild to fetch member instead of bot.get_user() so it will only show users in the guild
        options = [discord.SelectOption(label=self.ctx.guild.get_member(int(
            user.get('id'))).display_name, emoji=self.bot.get_emoji(911502994468651010), value=str(user.get('id'))) for user in all_users]

        super().__init__(placeholder='Choose your target...',
                            min_values=1, max_values=1, options=options)
        
    
    async def get_user(self, user: discord.Member) -> dict:
        """returns a user from the database"""
        return await self.bot.database.get_user(user=user)

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        user_id = int(self.values[0])
        user = self.ctx.guild.get_member(user_id)
        self.view.user= user
        embed, f = user_embed(await self.get_user(user), user)

       
        attachments = [] 
        if isinstance(f, discord.File):
            attachments = [f]
        if not self.ephemeral:
            await interaction.message.edit(embed=embed, view=self.view, attachments=attachments)
        else:
            await interaction.edit_original_response(embed=embed, view=self.view, attachments=attachments)

class Show_User_View(discord.ui.View):
    msg: discord.Message = None
    def __init__(self, ctx: commands.Context, bot: 'Oppy', user: discord.User, all_users: dict,  *, timeout: float = 180.0, ephemeral: bool = False):
        super().__init__(timeout=timeout)
        self.ctx = ctx
        self.user = user
        self.bot = bot
        self.add_item(Show_User_Dropdown(bot, self, all_users, ephemeral))
    
    @discord.ui.button(label="phone", style=discord.ButtonStyle.gray)
    async def send_phone(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(await self.bot.database.get_user_phone(self.user), ephemeral=True)

    async def on_timeout(self):
        for child in self.children:
            child.disabled = True
        await self.msg.edit(view=self)
        return self.stop()


class Confirmation_View(discord.ui.View):
    def __init__(self, *, timeout: float = 180.0):
        super().__init__(timeout=timeout)
        self.value = None


    @discord.ui.button(label='Confirm', style=discord.ButtonStyle.green)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.value = True
        button.disabled = True
        self.stop()
        

    @discord.ui.button(label='Cancel', style=discord.ButtonStyle.grey)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.value = False
        button.disabled = True
        self.stop()


    async def on_timeout(self):
        for child in self.children:
            child.disabled = True
        return self.stop()

