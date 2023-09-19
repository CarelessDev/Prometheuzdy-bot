import discord
import typing

import os, glob


def get_activity(activity_type: typing.Literal['gaming', 'listening', 'watching', 'competing', 'streaming'], activity_name: str, url: str = "https://www.youtube.com/watch?v=8VgSyKl9vg0"):
    if activity_type=='gaming':
        return discord.Game(name=activity_name)
    elif activity_type == 'streaming':
        return discord.Streaming(name=activity_name, url=url)
    else:
        return discord.Activity(type=getattr(discord.ActivityType, activity_type), name=activity_name)




initial_extensions = [os.path.splitext(name)[0].replace('\\', '.')  for name in glob.glob('cogs/*.py')]


description = """
It's Oppenheimer Style.
"""

activities = [get_activity('gaming', 'Plague inc.'), 
              get_activity('listening', 'to caveman sound'), 
              get_activity('watching', 'How to build a nuclear bomb'), 
              get_activity('competing', 'in a chess boxing match'), 
              get_activity('streaming', 'shrek', url='https://www.youtube.com/watch?v=8VgSyKl9vg0')]