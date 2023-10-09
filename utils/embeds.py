from __future__ import annotations
from main import Oppy
import discord
import os
import asyncio

from .pattern_check import image_path_check
from .promptpay import PromptPay

def qr_check(user_data: dict, user: discord.Member) -> tuple[str, discord.File]:
    f = discord.utils.MISSING                                   # default image, no qr image or promptpay token
    qr_url = user.avatar.url if user.avatar else discord.utils.MISSING # default image, no qr image or promptpay token
    if (qr:= user_data["promptpay_qr"]) != '0':   # if qr is not default
        if image_path_check(qr):                                                    # if qr is a path
            try:
                f = discord.File(qr, filename="qr.png")
                qr_url = f"attachment://qr.png"
                return qr_url, f
            except FileNotFoundError:
                pass
        else:                                                                       # if qr is a promptpay token
            f = discord.File(PromptPay.token2byte_QR(qr), filename="qr.png")
            qr_url = f"attachment://qr.png" 
    
    return qr_url, f

    

def user_embed(user_data: dict, user: discord.Member) -> tuple[discord.Embed, discord.File]:
    """Returns an embed for user information."""
    # TODO : when user does not have a qr image, generate one. Right now, error will be thrown "Not a well formed URL".
    qr_url, f = qr_check(user_data, user)        
        
    embed = (discord.Embed(title="Account Information", description=f"Account information for {user.mention}.", color=discord.Color.blurple())
             .set_author(name=user.name, icon_url=user.avatar.url if user.avatar else discord.utils.MISSING)
             .set_image(url=qr_url)
             .add_field(name="Phone Number", value=user_data['phone_number'], inline=True)
             .set_footer(text="dropdown will timeout in 3 minutes."))
    return embed, f

def qr_confirmation_embed(image_url: str, bot: discord.Client) -> discord.Embed:
    """Returns a tuple of embed and file for qr confirmation."""
    embed = (discord.Embed(title="QR Confirmation", description='Oppy uses a highly advance algorithm to check for valid qr image called "Trust me bro".\nSo, please check whether this is correct image.\nOtherwise, you will be severely punished by ASE congress', color=discord.Color.blurple())
             .set_author(name=bot.user.name, icon_url=bot.user.avatar.url)
             .set_image(url=image_url))
    return embed

