if __name__ == "__main__":
    import os, asyncio
    import asyncpg
    from settings import QR_PATH, credentials

    async def main():
        if not os.path.exists("data"):
            os.mkdir("data")
            print("Created data directory.")
        if not os.path.exists(QR_PATH):
            os.mkdir(QR_PATH)
            print("Created QR code directory.")

        async with asyncpg.create_pool(**credentials) as pool:

            await pool.execute('''CREATE TABLE IF NOT EXISTS guilds (
                                        id numeric PRIMARY KEY,
                               name text
                               );''')
            await pool.execute('''CREATE TABLE IF NOT EXISTS users (
                                        id numeric PRIMARY KEY,
                                        guild_id numeric NOT NULL,
                                        username text NOT NULL,
                                        phone_number text DEFAULT '0',
                                        promptpay_qr text DEFAULT '0',
                                        CONSTRAINT fk_guild_id
                                        FOREIGN KEY (guild_id)
                                        REFERENCES guilds(id)
                                        ON DELETE CASCADE
                                        );''')
    asyncio.run(main())
