import asyncio
import discord
import asyncpg
from discord.ext import commands
from core.config import CONFIG

async def getPrefix(client, message):
    if not getattr(message, "guild", None):
        return commands.when_mentioned_or(CONFIG.default_prefix)(client, message)

    row = await client.db.fetchrow(
        'SELECT prefix FROM ferroseed.guilds WHERE guild_id = $1',
        message.guild.id
    )
    if not row:
        await client.db.execute(
            'INSERT INTO ferroseed.guilds(guild_id, prefix) VALUES ($1, $2)',
            message.guild.id, CONFIG.default_prefix
        )
        return CONFIG.default_prefix
    return row["prefix"]

async def create_db_pool(bot: commands.Bot):
    bot.db = await asyncpg.create_pool(dsn=CONFIG.database_url, min_size=1, max_size=5)
    print("[db] pool ready")

async def load_extensions(bot: commands.Bot):
    # always-load base cogs first (add your own like cogs.events / cogs.ping when ready)
    base = []
    dynamic = [f"modules.{m}" for m in CONFIG.modules]
    for name in base + dynamic:
        try:
            await bot.load_extension(name)
            print(f"[ext] loaded {name}")
        except Exception as e:
            print(f"[ext] failed {name}: {e}")

async def main():
    intents = discord.Intents.default()
    intents.message_content = True
    intents.guilds = True
    # flip to True only if you actually need member events
    intents.members = False

    bot = commands.Bot(command_prefix=getPrefix, intents=intents)

    @bot.command()
    @commands.has_permissions(administrator=True)
    async def ping(ctx: commands.Context):
        ms = int(round(bot.latency * 1000))
        await ctx.reply(f"Command registered, latency: {ms} ms")

    try:
        await create_db_pool(bot)
        await load_extensions(bot)
        await bot.start(CONFIG.token)
    finally:
        try:
            await bot.db.close()
        except Exception:
            pass
        await bot.close()

if __name__ == "__main__":
    asyncio.run(main())
