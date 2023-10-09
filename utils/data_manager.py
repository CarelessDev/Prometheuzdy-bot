from __future__ import annotations
import aiomysql
import asyncio
import discord
import logging
import os
from typing import Coroutine, Optional, Union

from .pattern_check import phone_check
from .promptpay import PromptPay


QR_PATH = "data/qr_codes"



# logging.basicConfig(filename='logs/discord.log', level=logging.DEBUG)


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
        if not os.path.exists("data"):
            os.mkdir("data")
            logging.debug("Created data directory.")
        if not os.path.exists(QR_PATH):
            os.mkdir(QR_PATH)
            logging.debug("Created QR code directory.")

    async def __aenter__(self) -> Database_Manager:
        self.loop = asyncio.get_event_loop()
        self.pool = await aiomysql.create_pool(loop=self.loop, **self.__auth)
        # ensure that the database exists
        await self.create_database()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Close the database connection at exit."""
        self.pool.close()
        await self.pool.wait_closed()
        print("Database connection closed.")

    # ============================  helper  ========================================
    async def __execute(self, query: str, *args) -> None:
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(query, args)
                await conn.commit()
                
    async def __fetchall(self, query: str, *args) -> list:
        async with self.pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cur:
                await cur.execute(query, args)
                return await cur.fetchall()

    async def __fetchone(self, query: str, *args, to_dict:bool = True) -> Optional[tuple]:
        async with self.pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor if to_dict else aiomysql.Cursor) as cur:
                await cur.execute(query, args)
                return await cur.fetchone()

    async def __create_table(self, table: str, columns: str) -> None:
        await self.__execute(f"CREATE TABLE IF NOT EXISTS {table} ({columns})")

    # =========================== create functions ================================

    async def create_database(self):
        """database per guild"""
        await self.__create_table("guilds", """id BIGINT NOT NULL PRIMARY KEY, 
                                  guild_name VARCHAR(100) NOT NULL""")
        await self.__create_table("users", """id BIGINT NOT NULL, 
                                  guild_id BIGINT NOT NULL, 
                                  user_name VARCHAR(32) NOT NULL,
                                  phone_number VARCHAR(20) DEFAULT '0', 
                                  promptpay_qr VARCHAR(255) DEFAULT '0',
                                  FOREIGN KEY (guild_id) REFERENCES guilds(id) ON DELETE CASCADE""")

    async def create_guild(self, guild: discord.Guild): 
        try:
            await self.__execute("INSERT INTO guilds (id, guild_name) VALUES (%s, %s)",
                                guild.id, guild.name)
            logging.info(f"Created guild {guild.name} in database")
        except aiomysql.IntegrityError:
            logging.info(f"Guild {guild.name} already exists in database")
        
        

    async def create_user(self, user: discord.Member):
        """create user in database"""
        try:
            await self.__execute("INSERT INTO users (id, guild_id, user_name) VALUES (%s, %s, %s)",
                                user.id, user.guild.id, user.name)
        except aiomysql.IntegrityError:
            pass
            
    # =========================== read functions ================================
    async def get_guild(self, guild_id: Optional[int] = None):
        if guild_id:
            return await self.__fetchone("SELECT * FROM guilds WHERE id = %s", guild_id)
        return await self.__fetchall("SELECT * FROM guilds")
    
    async def get_user(self, user: Optional[discord.Member]=None, guild_id: Optional[int]=None) -> Union[dict, list[dict], None]:
        if user:
            return await self.__fetchone("SELECT * FROM users WHERE id = %s AND guild_id = %s", user.id, user.guild.id)
        elif guild_id:
            return await self.__fetchall("SELECT * FROM users WHERE guild_id = %s", guild_id)
        return await self.__fetchall("SELECT * FROM users")
    
    async def get_user_phone(self, user: discord.Member) -> str:
        if (phone := await self.__fetchone("SELECT phone_number FROM users WHERE id = %s AND guild_id = %s", user.id, user.guild.id, to_dict=False)):
            return phone[0]
        return None
    
    async def get_user_qr(self, user: discord.Member) -> str:
        if (qr := await self.__fetchone("SELECT promptpay_qr FROM users WHERE id = %s AND guild_id = %s", user.id, user.guild.id, to_dict=False)):
            return qr[0]
        return None


    # =========================== update functions ================================
    async def set_phone(self, user: discord.Member, phone: str) -> [False, str]:
        if not (p := phone_check(phone)):
            return False
        await self.__execute("UPDATE users SET phone_number = %s WHERE id = %s AND guild_id = %s", p, user.id, user.guild.id)
        await self.__execute("UPDATE users SET promptpay_qr = %s WHERE id = %s AND guild_id = %s", str(PromptPay(p)), user.id, user.guild.id)
        return p

    async def set_promptpay_qr(self, user: discord.Member, qr: str):
        await self.__execute("UPDATE users SET promptpay_qr = %s WHERE id = %s AND guild_id = %s", qr, user.id, user.guild.id)

    # =========================== delete functions ================================





if __name__ == "__main__":
    # db = DB_Manager()
    # # db.create_user(u)
    # u = User(123, "test", "0", "0")
    # db.create_user(u)
    # db.update_phone(123, "1234567890")
    pass
