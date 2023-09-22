from __future__ import annotations
from discord import HTTPException, app_commands
from discord.ext import commands
import discord
from utils.data_manager import User
import typing

from utils.embeds import user_embed


class Citizen(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.ctx_menu = app_commands.ContextMenu(
            name='set phone number',
            callback=self.set_phone_from_message,
        )
        self.bot.tree.add_command(self.ctx_menu)
        self._routine = {}

    async def cog_unload(self) -> None:
        self.bot.tree.remove_command(
            self.ctx_menu.name, type=self.ctx_menu.type)

    async def set_phone_from_message(self, ctx: discord.Interaction, message: discord.Message) -> None:
        user_id = message.author.id
        if not self.bot.database.check_user(user_id):
            u = User(user_id, message.author.name, "0", "0")
            self.bot.database.create_user(u)
        user = message.author
        phone = message.content
        if (p := self.bot.database.update_phone(user_id, phone)):
            await ctx.response.send_message(f"Set phone number for {user.name} to {p}.")
        else:
            await ctx.response.send_message(f"Invalid phone number.")

    @commands.hybrid_command()
    async def create_account(self, ctx: commands.Context, user: discord.User, ephemeral: bool = False):
        """Creates a new account."""
        u = User(user.id, user.name, "0", "0")
        self.bot.database.create_user(u)
        await ctx.send(f"Created account for {user.name}.", ephemeral=ephemeral)

    @commands.hybrid_command()
    async def set_phone(self, ctx: commands.Context, phone: str, user: typing.Union[discord.User, None], ephemeral: bool = False):
        """Sets the phone number for a user."""
        if not user:
            user = ctx.author
        user_id = user.id
        if not self.bot.database.check_user(user_id):
            u = User(user_id, user.name, "0", "0")
            self.bot.database.create_user(u)
        if (p := self.bot.database.update_phone(user_id, phone)):
            await ctx.send(f"Set phone number for {user.name} to {p}.", ephemeral=ephemeral)
        else:
            await ctx.send(f"Invalid phone number.", ephemeral=ephemeral)

    @app_commands.command()
    async def show_user(self, ctx: discord.Interaction, user: discord.User, ephemeral: bool = False):
        """Shows the user's account information."""
        await ctx.response.defer(ephemeral=ephemeral)
        try:
            if (old := self._routine.get(ctx.user.id)):
                m, v = old
                await v.on_timeout()
                await m.edit(view=v)
        except HTTPException:
            pass

        all_users = self.bot.database.get_user()

        class View(discord.ui.View):
            def __init__(self, bot, *, timeout: float = 180.0):
                super().__init__(timeout=timeout)

                class Dropdown(discord.ui.Select):
                    def __init__(self, bot: commands.Bot):
                        self.bot = bot

                        # dropdown menus
                        # using guild to fetch member instead of bot.get_user() so it will only show users in the guild
                        options = [discord.SelectOption(label=ctx.guild.get_member(int(
                            uid)).display_name, emoji=self.bot.get_emoji(911502994468651010), value=uid) for uid in all_users]

                        super().__init__(placeholder='Choose your target...',
                                         min_values=1, max_values=1, options=options)

                    async def callback(self, interaction: discord.Interaction):
                        await interaction.response.defer()
                        user_id = int(self.values[0])
                        embed = user_embed(all_users[str(user_id)], self.bot)
                        if not ephemeral:
                            await interaction.message.edit(embed=embed, view=self.view)
                        else:
                            await interaction.edit_original_response(embed=embed, view=self.view)

                self.add_item(Dropdown(bot))

            async def on_timeout(self):
                for child in self.children:
                    child.disabled = True
                await msg.edit(view=self)
                return self.stop()

        view = View(self.bot)

        user_id = user.id
        if str(user_id) in all_users:
            embed = user_embed(all_users[str(user_id)], self.bot)
            msg = await ctx.followup.send(embed=embed, view=view, ephemeral=ephemeral)
        else:
            msg = await ctx.followup.send(f"{user.name} does not have an account.", view=view, ephemeral=ephemeral)

        self._routine[ctx.user.id] = [msg, view]


async def setup(bot: commands.Bot):
    await bot.add_cog(Citizen(bot))
