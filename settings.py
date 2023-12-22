import discord
import typing

import os
import glob
from dotenv import load_dotenv

load_dotenv()


def get_activity(activity_type: typing.Literal['gaming', 'listening', 'watching', 'competing', 'streaming'], activity_name: str, url: str = "https://www.youtube.com/watch?v=8VgSyKl9vg0"):
    if activity_type == 'gaming':
        return discord.Game(name=activity_name)
    elif activity_type == 'streaming':
        return discord.Streaming(name=activity_name, url=url)
    else:
        return discord.Activity(type=getattr(discord.ActivityType, activity_type), name=activity_name)


initial_extensions = ['.'.join(os.path.split(path)).removesuffix(
    '.py') for path in glob.glob('cogs/*.py')]


description = """
It's Oppenheimer Style.
"""

activities = [get_activity('gaming', 'with your wife'),
              get_activity('listening', 'to the voices in my head'),
              get_activity('watching', 'the world burn'),
              get_activity('competing', 'in the Oppenheimer Style Olympics'),
              get_activity('streaming', 'shrek 2',
                           url='https://www.youtube.com/watch?v=8VgSyKl9vg0'),
              get_activity('listening', 'theory will only take you so far')]

QR_PATH = "data/qr_codes"

credentials = {'host': os.environ.get("DB_HOST"),  # database connection
               'port': int(os.environ.get("DB_PORT")),
               'user': "zu2",
               'password': 'Oppy987',
               'database': 'oppybot'}
