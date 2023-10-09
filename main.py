import discord
import logging
import logging.handlers
import traceback
import sys
import os
import asyncio

from discord.ext import commands, tasks
from dotenv import load_dotenv
from random import choice
from aiohttp import ClientSession

from utils.data_manager import Database_Manager
from settings import description, get_activity, initial_extensions, activities

load_dotenv()

print(os.environ.get("DB_PASS"))

class Oppy(commands.Bot):
    def __init__(self, database_manager: Database_Manager, testing_guild_id: int = None):
        super().__init__(
            command_prefix=commands.when_mentioned_or('oppydo '),
            description=description,
            pm_help=None,
            help_attrs=dict(hidden=True),
            chunk_guilds_at_startup=False,
            heartbeat_timeout=150.0,
            intents=discord.Intents.all(),
            enable_debug_events=True,
        )
        self.testing_guild_id = testing_guild_id
        self.CLIENT_ID = os.environ.get('CLIENT_ID')
        self.database = database_manager

    async def setup_hook(self):
        for extension in initial_extensions:
            try:
                await self.load_extension(extension)

            except Exception as e:
                print(
                    f'Failed to load extension {extension}.', file=sys.stderr)
                traceback.print_exc()

        # This would also be a good place to connect to our database and
        # load anything that should be in memory prior to handling events.
        # Basically: don't 👏 do 👏 shit 👏 in 👏 on_ready. -R. Danny
        async for guild in self.fetch_guilds(limit=None):
            await self.database.create_guild(guild)

        # In this case, we are using this to ensure that once we are connected, we sync for the testing guild.
        # You should not do this for every guild or for global sync, those should only be synced when changes happen.
        if self.testing_guild_id:
            guild = discord.Object(self.testing_guild_id)
            try: 
                # We'll copy in the global commands to test with:
                self.tree.copy_global_to(guild=guild)
                # followed by syncing to the testing guild.
                await self.tree.sync(guild=guild)
            except discord.errors.Forbidden as e:
                logging.warn(e)

    async def on_ready(self):
        if getattr(self, 'background_task', False):
            await self.background_task()
        print(f'Logged in as {self.user} (ID: {self.user.id})')
        print('------')

    @tasks.loop(seconds=300)
    async def background_task(self):
        await self.change_presence(activity=choice(activities))


async def main():
    # When taking over how the bot process is run, you become responsible for a few additional things.
    # 1. logging
    handler = logging.handlers.RotatingFileHandler(
        filename='logs/discord.log',
        encoding='utf-8',
        maxBytes=32 * 1024 * 1024,  # 32 MiB
        backupCount=5,  # Rotate through 5 files
    )
    dt_fmt = '%Y-%m-%d %H:%M:%S'
    formatter = logging.Formatter(
        '[{asctime}] [{levelname:<8}] {name}: {message}', dt_fmt, style='{')
    handler.setFormatter(formatter)
    discord.utils.setup_logging(handler=handler, root=False)

    # One of the reasons to take over more of the process though
    # is to ensure use with other libraries or tools which also require their own cleanup.

    # Here we have a database pool, which do cleanup at exit.
    # We also have our bot, which depends on both of these.
    async with Database_Manager(host=os.environ.get("DB_HOST"),  # database connection
                                port=int(os.environ.get("DB_PORT")),                
                                user=os.environ.get("DB_USER"),
                                password=os.environ.get("DB_PASS"),
                                db=os.environ.get("DB_NAME")) as db_manager:
        # 2. We become responsible for starting the bot.
        async with Oppy(database_manager=db_manager) as bot:
            await bot.start(os.environ.get("TOKEN"))

if __name__ == "__main__":
    asyncio.run(main())
    
