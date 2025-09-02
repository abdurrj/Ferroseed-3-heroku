import asyncio
import discord
from discord.ext import commands

from core.config import CONFIG
from core.prefix import get_prefix
from core.db import create_pool, close_pool, attach_pool
from core.extensions import load_all_extensions

async def main():
    intents = discord.Intents.default()
    intents.message_content = True
    intents.guilds = True
    intents.members = False  # flip True only if you need it

    bot = commands.Bot(command_prefix=get_prefix, intents=intents)

    pool = await create_pool()
    attach_pool(bot, pool)

    try:
        await load_all_extensions(bot)   # reads enabled modules from application.yml
        await bot.start(CONFIG.token)
    finally:
        await close_pool(pool)
        await bot.close()

if __name__ == "__main__":
    asyncio.run(main())
