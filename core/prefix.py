from discord.ext import commands
from core.config import CONFIG

async def get_prefix(bot: commands.Bot, message):
    default = CONFIG.default_prefix
    if not getattr(message, "guild", None):
        return commands.when_mentioned_or(default)(bot, message)
    try:
        row = await bot.db.fetchrow(
            'SELECT prefix FROM ferroseed.guilds WHERE guild_id = $1',
            message.guild.id
        )
        if not row:
            await bot.db.execute(
                'INSERT INTO ferroseed.guilds(guild_id, prefix) VALUES ($1, $2)',
                message.guild.id, default
            )
            return default
        return row["prefix"]
    except Exception as e:
        print(f"[prefix] DB error for guild {getattr(message.guild, 'id', '?')}: {e}")
        return default
