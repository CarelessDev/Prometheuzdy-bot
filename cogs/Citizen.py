from __future__ import annotations
from main import Oppy
from discord import HTTPException, app_commands
from discord.ext import commands
import discord
import typing, os



from settings import QR_PATH
from utils.embeds import user_embed, qr_confirmation_embed
from utils.views import Show_User_View, Confirmation_View
from utils.promptpay import PromptPay
from utils.pattern_check import image_path_check

class Citizen(commands.Cog):
    def __init__(self, bot: 'Oppy') -> None:
        self.bot = bot
        self._routine = {}

    async def cog_unload(self) -> None:
        self.bot.tree.remove_command(
            self.ctx_menu.name, type=self.ctx_menu.type)
        
    # general functions ====================================================================================================

    async def __ensure_user(self, user: discord.User) -> None:
        """Ensures that a user exists in the database."""
        if not await self.bot.database.get_user(user=user):
            await self.bot.database.create_user(user)

        
    async def __set_phone(self, interaction: discord.Interaction, phone: str, user: typing.Union[discord.Member, None], ephemeral: bool = False):
        """Sets the phone number for a user."""
        if not user:
            user = interaction.user
        await self.__ensure_user(user)
        if (p := await self.bot.database.set_phone(user, phone)):
            await interaction.response.send_message(f"Set phone number for {user.name} to {p}.", ephemeral=ephemeral)
        else:
            await interaction.response.send_message(f"Invalid phone number.", ephemeral=ephemeral)

        
    async def __show_user(self, interaction: discord.Interaction, user: discord.Member, ephemeral: bool = False):
        """Shows the user's account information."""
        await interaction.response.defer(ephemeral=ephemeral)
        await self.__ensure_user(user)
        try:
            if (old := self._routine.get(interaction.user.id)):
                m, v = old
                await v.on_timeout()
                await m.edit(view=v)
        except HTTPException:
            pass

        all_users = await self.bot.database.get_user(guild_id=interaction.guild.id)
        
        view = Show_User_View(interaction, self.bot, user, all_users, timeout=180.0, ephemeral=ephemeral)

        if (u := await self.bot.database.get_user(user=user)):
            embed, f = user_embed(u, user)
            msg = await interaction.followup.send(embed=embed, view=view, ephemeral=ephemeral, file=f)
        else:
            msg = await interaction.followup.send(f"{user.name} does not have an account.", view=view, ephemeral=ephemeral)
        view.msg = msg
        # sender id: [message, view]
        self._routine[interaction.user.id] = [msg, view]

    
    async def __set_qr(self, interaction: discord.Interaction, qr: discord.Attachment, user: discord.User, ephemeral: bool):
        await self.__ensure_user(user)
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
            qr_path = os.path.join(QR_PATH, f"{user.id}.png")
            await qr.save(qr_path)
            await self.bot.database.set_promptpay_qr(user, qr_path)
        else:
            if not ephemeral:
                await interaction.message.edit(content="Cancelled.", view=None, embed=None)
            else:
                await interaction.edit_original_response(content="Cancelled.", view=None, embed=None)

    # slash and context commands ====================================================================================================

    @commands.hybrid_command()
    async def create_account(self, ctx: commands.Context, user: discord.Member, ephemeral: bool = False):
        """Creates a new account."""
        await self.__ensure_user(user)
        await ctx.send(f"Created account for {user.name}.", ephemeral=ephemeral)
   
    @app_commands.command()
    async def set_phone(self, ctx: commands.Context, phone: str, user: typing.Union[discord.Member, None], ephemeral: bool = False):
        """Sets the phone number for a user."""
        await self.__set_phone(ctx, phone, user, ephemeral)

    @app_commands.command()
    async def show_user(self, interaction: discord.Interaction, user: discord.Member, ephemeral: bool = False):
        """Shows the user's account information."""
        await self.__show_user(interaction, user, ephemeral)

    @app_commands.command()
    async def set_qr(self, interaction: discord.Interaction, qr: discord.Attachment, user: typing.Union[discord.User, None], ephemeral: bool = True):
        """Sets the QR code for a user. If no user is specified, the user who invoked the command will be used."""
        if not user:
            user = interaction.user
        await self.__set_qr(interaction, qr, user, ephemeral)

    @app_commands.command()
    async def pay(self, interaction: discord.Interaction, amount: float = 0.00, user: typing.Union[discord.User, None] = None):
        """Generate Promptpay QR code for a user. If no user is specified, the user who invoked the command will be used."""
        if not user:
            user = interaction.user
        await self.__ensure_user(user)
        content = f"```Paying {user.display_name} {amount} Baht```" if amount else f"Paying {user.display_name}"
        if (qr:= await self.bot.database.get_user_qr(user)) != '0' and image_path_check(qr):
            print('qr found')
            await interaction.response.send_message(content=content, file=discord.File(fp=qr, filename="qr.png"))
        elif (p := await self.bot.database.get_user_phone(user)) != '0':
            await interaction.response.send_message(content=content, file=discord.File(fp=PromptPay.to_byte_QR(p, amount), filename="qr.png"))
        else:
            await interaction.response.send_message("User has not set their phone number or QR image.")
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
