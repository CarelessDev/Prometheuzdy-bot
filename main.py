import discord
import traceback
import sys
import os
from discord.ext import commands, tasks
from dotenv import load_dotenv
from random import choice

from utils.data_manager import DB_Manager
from settings import description, get_activity, initial_extensions, activities


class Oppy(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix=commands.when_mentioned_or('o!'),
            description=description,
            pm_help=None,
            help_attrs=dict(hidden=True),
            chunk_guilds_at_startup=False,
            heartbeat_timeout=150.0,
            intents=discord.Intents.all(),
            enable_debug_events=True,
            activity=get_activity('playing', 'with your wife'),
        )
        self.CLIENT_ID = os.environ.get('CLIENT_ID')
        self.database = DB_Manager()

    async def setup_hook(self):
        for extension in initial_extensions:
            try:
                await self.load_extension(extension)

            except Exception as e:
                print(
                    f'Failed to load extension {extension}.', file=sys.stderr)
                traceback.print_exc()
        fmt = await bot.tree.sync()

    async def on_ready(self):
        if getattr(self, 'background_task', False):
            await self.background_task()
        print(f'Logged in as {self.user} (ID: {self.user.id})')
        print('------')

    @tasks.loop(seconds=300)
    async def background_task(self):
        await bot.change_presence(activity=choice(activities))


if __name__ == "__main__":
    load_dotenv()
    bot = Oppy()
    bot.run(os.environ.get('TOKEN'))
