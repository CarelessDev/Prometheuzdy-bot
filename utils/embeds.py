import discord

def user_embed(user_data: dict, bot: discord.Client) -> tuple[discord.Embed, discord.File]:
    """Returns an embed for user information."""
    uid = int(user_data['id'])
    user = bot.get_user(uid)
    f = discord.utils.MISSING
    qr_url = user.avatar.url
    if (qr:= user_data.get('qr')):
        try: 
            f = discord.File(qr, filename="qr.png")
            qr_url = "attachment://qr.png"
        except FileNotFoundError:
            pass
            
        
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

# def user_embed(user_data, bot):
#     uid = int(user_data['id'])
#     user = bot.get_user(uid)
#     if (qr:= user_data.get('qr')):
#         f = discord.File(qr, filename="qr.png")
#         qr_url = "attachment://qr.png"
#     else:
#         f = discord.utils.MISSING
#         qr_url = user.avatar.url
#     embed = (discord.Embed(title="Account Information", description=f"Account information for {user.mention}.", color=discord.Color.blurple())
#              .set_author(name=user.name, icon_url=user.avatar.url)
#              .set_image(url=qr_url)
#              .add_field(name="Phone Number", value=user_data['phone'], inline=True)
#              .add_field(name="Account Number", value=user_data['account_number'], inline=True)
#              .set_footer(text="dropdown will timeout in 3 minutes."))
#     return embed, f
