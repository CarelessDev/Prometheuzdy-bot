from __future__ import annotations
from discord import HTTPException, app_commands
from discord.ext import commands
import discord
import typing, os


from utils.data_manager import User, QR_PATH
from utils.embeds import user_embed, qr_confirmation_embed
from utils.views import Show_User_View, Confirmation_View

class Citizen(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        set_phone = app_commands.ContextMenu(
            name='set phone number',
            callback=self.set_phone_from_message,
        )
        set_qr = app_commands.ContextMenu(
            name='set qr code',
            callback=self.set_qr_from_message,
        )
        self.bot.tree.add_command(set_phone)
        self.bot.tree.add_command(set_qr)
        self._routine = {}

    async def cog_unload(self) -> None:
        self.bot.tree.remove_command(
            self.ctx_menu.name, type=self.ctx_menu.type)
        
    # general functions ====================================================================================================

    def __ensure_user(self, user: discord.User) -> User:
        """Ensures that a user exists in the database."""
        if not self.bot.database.check_user(user.id):
            u = User(user.id, user.name, "0", "0")
            self.bot.database.create_user(u)

        
    async def __set_phone(self, ctx: commands.Context, phone: str, user: typing.Union[discord.User, None], ephemeral: bool = False):
        """Sets the phone number for a user."""
        if not user:
            user = ctx.author
        self.__ensure_user(user)
        if (p := self.bot.database.set_phone(user.id, phone)):
            await ctx.send(f"Set phone number for {user.name} to {p}.", ephemeral=ephemeral)
        else:
            await ctx.send(f"Invalid phone number.", ephemeral=ephemeral)

        
    async def __show_user(self, ctx: discord.Interaction, user: discord.User, ephemeral: bool = False):
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

        view = Show_User_View(ctx, self.bot, all_users, user, timeout=180.0, ephemeral=ephemeral)

        user_id = user.id
        if str(user_id) in all_users:
            embed, f = user_embed(all_users[str(user_id)], self.bot)
            msg = await ctx.followup.send(embed=embed, view=view, ephemeral=ephemeral, file=f)
        else:
            msg = await ctx.followup.send(f"{user.name} does not have an account.", view=view, ephemeral=ephemeral, file=f)
        view.msg = msg

        self._routine[ctx.user.id] = [msg, view]

    
    async def __set_qr(self, interaction: discord.Interaction, qr: discord.Attachment, user: discord.User, ephemeral: bool):
        self.__ensure_user(user)
        # confirmation 
        embed = qr_confirmation_embed(qr.proxy_url, self.bot)
        view = Confirmation_View(timeout=5.0)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=ephemeral)
            
        await view.wait()
        # discord does not trigger any even when user press dismiss message
        if view.value is None:
            # quietly terminate this function from time out
            if not ephemeral:
                await interaction.message.edit(content="timeout", embed=None)
            else:
                await interaction.edit_original_response(content="timeout", embed=None)
            return
        elif view.value:
            # update qr code
            embed.title = "QR code updated."
            embed.description = "QR code updated successfully."
            if not ephemeral:
                await interaction.message.edit(view=None, embed=embed)
            else:
                await interaction.edit_original_response(view=None, embed=embed)
            await qr.save(os.path.join(QR_PATH, f"{user.id}.png"))
            self.bot.database.set_qr(user.id)
        else:
            if not ephemeral:
                await interaction.message.edit(content="Cancelled.", view=None, embed=None)
            else:
                await interaction.edit_original_response(content="Cancelled.", view=None, embed=None)

    # message menu commands ====================================================================================================

    async def set_phone_from_message(self, interaction: discord.Interaction, message: discord.Message) -> None:
        user = message.author
        self.__ensure_user(user)
        phone = message.content
        await self._set_phone(interaction, phone, user)

    async def set_qr_from_message(self, interaction: discord.Interaction, message: discord.Message) -> None:
        user = message.author
        self.__ensure_user(user)
        # TODO: check if the attachment is in the message

    # slash and context commands ====================================================================================================

    @commands.hybrid_command()
    async def create_account(self, ctx: commands.Context, user: discord.User, ephemeral: bool = False):
        """Creates a new account."""
        u = User(user.id, user.name, "0", "0")
        self.bot.database.create_user(u)
        await ctx.send(f"Created account for {user.name}.", ephemeral=ephemeral)
   
    @commands.hybrid_command()
    async def set_phone(self, ctx: commands.Context, phone: str, user: typing.Union[discord.User, None], ephemeral: bool = False):
        """Sets the phone number for a user."""
        await self.__set_phone(ctx, phone, user, ephemeral)

    @app_commands.command()
    async def show_user(self, ctx: discord.Interaction, user: discord.User, ephemeral: bool = False):
        """Shows the user's account information."""
        await self.__show_user(ctx, user, ephemeral)

    @app_commands.command()
    async def set_qr(self, interaction: discord.Interaction, qr: discord.Attachment, user: typing.Union[discord.User, None], ephemeral: bool = True):
        """Sets the QR code for a user. If no user is specified, the user who invoked the command will be used."""
        if not user:
            user = interaction.user
        await self.__set_qr(interaction, qr, user, ephemeral)

    # event listeners ====================================================================================================

    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error):
        # This prevents any cogs with an overwritten cog_command_error being handled here.
        cog = ctx.cog
        if cog:
            if cog._get_overridden_method(cog.cog_command_error) is not None:
                return
        ignored = (commands.CommandNotFound, )
         # Allows us to check for original exceptions raised and sent to CommandInvokeError.
        # If nothing is found. We keep the exception passed to on_command_error.
        error = getattr(error, 'original', error)
        await ctx.send(error)



async def setup(bot: commands.Bot):
    await bot.add_cog(Citizen(bot))
