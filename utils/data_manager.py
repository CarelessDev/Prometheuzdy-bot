from __future__ import annotations
import asyncpg
import asyncio
import discord
import logging
import os, sys, traceback
from typing import Coroutine, Optional, Union

from .pattern_check import phone_check
from .promptpay import PromptPay


def log_data(func):
    def wrapper(*args, **kwargs):
        logging.debug(
            f"Function {func.__name__} called. get_data() returned {args[0].get_data()}.")
        return func(*args, **kwargs)
    return wrapper

class Database_Manager:
    # ============================  init  ========================================
    def __init__(self, **kwargs) -> None:
        self.__auth = kwargs
        
    async def __aenter__(self) -> Database_Manager:
        self.loop = asyncio.get_event_loop()
        self.pool = await asyncpg.create_pool(**self.__auth, loop=self.loop)
        # ensure that the database exists
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Close the database connection at exit."""
        await self.pool.close()
        print("Database connection closed.")
   
    # =========================== create functions ================================
        
    async def create_guild(self, guild: discord.Guild):
        """create guild"""
        try:
            await self.pool.execute('''INSERT INTO guilds (id, name) VALUES ($1, $2)
                                    ON CONFLICT (id)
                                    DO NOTHING;''', int(guild.id), guild.name)
        except Exception as e:
            logging.error(traceback.format_exc())
    
    async def create_user(self, user: discord.User):
        """create user"""
        try:
            await self.pool.execute('''INSERT INTO users (id, guild_id, username) VALUES ($1, $2, $3)
                                    ON CONFLICT (id)
                                    DO NOTHING;''', int(user.id), int(user.guild.id), user.name)
        except Exception as e:
            logging.error(traceback.format_exc())

    async def get_user(self, user: Optional[discord.Member]=None, guild_id: Optional[int]=None) -> Union[dict, list[dict], None]:
        """get user"""
        if user:
            return await self.pool.fetchrow('''SELECT * FROM users WHERE id = $1 AND guild_id = $2;''', int(user.id), int(user.guild.id))
        elif guild_id:
            return await self.pool.fetch('''SELECT * FROM users WHERE guild_id = $1;''', int(guild_id))
        return await self.pool.fetch('''SELECT * FROM users;''')
    

    async def get_user_phone(self, user: discord.User) -> str:
        """get user phone"""
        return await self.pool.fetchval('''SELECT phone_number FROM users WHERE id = $1 AND guild_id = $2;''', int(user.id), int(user.guild.id))
    
    async def get_user_qr(self, user: discord.User) -> str:
        """get user promptpay"""
        if (qr := await self.pool.fetchval('''SELECT promptpay_qr FROM users WHERE id = $1 AND guild_id = $2;''', int(user.id), int(user.guild.id))):
            return qr
        return '0'
    
     # =========================== update functions ================================
    async def set_phone(self, user: discord.Member, phone: str) -> [False, str]:
        if not (p := phone_check(phone)):
            return False
        
        await self.pool.execute("UPDATE users SET phone_number = $1 WHERE id = $2 AND guild_id = $3", p, user.id, user.guild.id)
        await self.pool.execute("UPDATE users SET promptpay_qr = $1 WHERE id = $2 AND guild_id = $3", str(PromptPay(p)), user.id, user.guild.id)
        return p

    async def set_promptpay_qr(self, user: discord.Member, qr: str):
        await self.pool.execute("UPDATE users SET promptpay_qr = $1 WHERE id = $1 AND guild_id = $3", qr, user.id, user.guild.id)

   