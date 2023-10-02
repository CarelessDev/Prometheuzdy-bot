from __future__ import annotations
import discord
from discord.ext import commands
from .embeds import user_embed


class Show_User_Dropdown(discord.ui.Select):
    def __init__(self, bot: commands.Bot, view: Show_User_View, ephemeral: bool):
        self._view = view
        self.bot = bot
        self.ctx = self.view.ctx
        self.all_users = self.view.all_users
        self.ephemeral = ephemeral
        # dropdown menus
        # using guild to fetch member instead of bot.get_user() so it will only show users in the guild
        options = [discord.SelectOption(label=self.ctx.guild.get_member(int(
            uid)).display_name, emoji=self.bot.get_emoji(911502994468651010), value=uid) for uid in self.all_users if self.ctx.guild.get_member(int(
            uid))]

        super().__init__(placeholder='Choose your target...',
                            min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        user_id = int(self.values[0])
        self.view.user_id = user_id
        embed, f = user_embed(self.all_users[str(user_id)], self.bot)
       
        attachments = [] 
        if isinstance(f, discord.File):
            attachments = [f]
        if not self.ephemeral:
            await interaction.message.edit(embed=embed, view=self.view, attachments=attachments)
        else:
            await interaction.edit_original_response(embed=embed, view=self.view, attachments=attachments)

class Show_User_View(discord.ui.View):
    msg: discord.Message = None
    def __init__(self, ctx: commands.Context, bot, all_users: dict, user: discord.User, *, timeout: float = 180.0, ephemeral: bool = False):
        super().__init__(timeout=timeout)
        self.ctx = ctx
        self.all_users = all_users
        self.user_id = user.id

        self.add_item(Show_User_Dropdown(bot, self, ephemeral))
    
    @discord.ui.button(label="phone", style=discord.ButtonStyle.gray)
    async def send_phone(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(self.all_users[str(self.user_id)]['phone'], ephemeral=True)

    @discord.ui.button(label="qr", style=discord.ButtonStyle.gray)
    async def send_qr(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            await interaction.response.send_message(None, file=discord.File(f"data/qr_codes/{self.user_id}.png"), ephemeral=True)
        except FileNotFoundError:
            await interaction.response.send_message("QR was not found.", ephemeral=True)

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

