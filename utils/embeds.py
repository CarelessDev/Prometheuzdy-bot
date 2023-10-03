import discord
import os

from .pattern_check import qr_image_path_check
from .promptpay import PromptPay

def qr_check(bot: discord.Client, user: discord.User):
    f = discord.utils.MISSING                                   # default image, no qr image or promptpay token
    qr_url = user.avatar.url
    if (qr:= bot.database.get_user(user.id).get('qr')):         # piority 1: if user has qr image
        if qr_image_path_check(os.path.split(qr)[-1]):
            try:                                                
                f = discord.File(qr, filename="qr.png")         
                qr_url = "attachment://qr.png"
                return qr_url, f
            except FileNotFoundError:
                pass                                            # if qr image does not exist,  go to second piority
            
        
    if (qr:= bot.database.get_user(user.id).get('promptpay_token')):        # piority 2: if user has promptpay token
        qr = PromptPay.token2byte_QR(qr)                    # default qr code with no specific money request
        f = discord.File(qr, filename="qr.png")
        qr_url = f"attachment://qr.png"
    return qr_url, f

    

def user_embed(user_data: dict, bot: discord.Client) -> tuple[discord.Embed, discord.File]:
    """Returns an embed for user information."""
    uid = int(user_data['id'])
    user = bot.get_user(uid)
    qr_url, f = qr_check(bot, user)
    
            
        
    embed = (discord.Embed(title="Account Information", description=f"Account information for {user.mention}.", color=discord.Color.blurple())
             .set_author(name=user.name, icon_url=user.avatar.url)
             .set_image(url=qr_url)
             .add_field(name="Phone Number", value=user_data['phone'], inline=True)
             .add_field(name="Account Number", value=user_data['account_number'], inline=True)
             .set_footer(text="dropdown will timeout in 3 minutes."))
    return embed, f

def qr_confirmation_embed(image_url: str, bot: discord.Client) -> discord.Embed:
    """Returns a tuple of embed and file for qr confirmation."""
    embed = (discord.Embed(title="QR Confirmation", description='Oppy uses a highly advance algorithm to check for valid qr image called "Trust me bro".\nSo, please check whether this is correct image.\nOtherwise, you will be severely punished by ASE congress', color=discord.Color.blurple())
             .set_author(name=bot.user.name, icon_url=bot.user.avatar.url)
             .set_image(url=image_url))
    return embed

