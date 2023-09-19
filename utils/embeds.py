import discord



def user_embed(user_data, bot):
    uid = int(user_data['id'])
    user = bot.get_user(uid)
    embed = (discord.Embed(title="Account Information", description=f"Account information for {user.mention}.", color=discord.Color.blurple())
                 .add_field(name="Name", value=user.name, inline=True)
                .add_field( name="Discriminator", value=user.discriminator, inline=True)
                .add_field( name="Phone Number", value=user_data['phone'], inline=True)
                .add_field(name="Account Number", value=user_data['account_number'], inline=True)
                .set_image(url=user.avatar.url)
                 .set_footer(text="dropdown will timeout in 3 minutes."))
    return embed


def payment_embed(user_data, bot):
    pass