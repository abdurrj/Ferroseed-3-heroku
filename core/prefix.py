# core/prefix.py
from __future__ import annotations

from typing import Optional
from discord.ext import commands
from core.config import CONFIG

async def get_prefix(bot: commands.Bot, message) -> str:
    """
    Dynamic per-guild prefix with safe fallback.
    - DMs: mention-or-default
    - Guilds: read from ferroseed.guilds; insert default if missing
    - On DB error: fall back to CONFIG.default_prefix (no crash)
    """
    default = CONFIG.default_prefix

    # Direct messages: allow mention or default prefix
    if not getattr(message, "guild", None):
        return commands.when_mentioned_or(default)(bot, message)

    try:
        row = await bot.db.fetchrow(
            'SELECT prefix FROM ferroseed.guilds WHERE guild_id = $1',
            message.guild.id
        )
        if not row:
            # Insert a default row for this guild
            await bot.db.execute(
                'INSERT INTO ferroseed.guilds(guild_id, prefix) VALUES ($1, $2)',
                message.guild.id, default
            )
            return default
        return row["prefix"]
    except Exception as e:
        # Don’t break commands if DB is temporarily unavailable
        print(f"[prefix] DB error for guild {getattr(message.guild, 'id', '?')}: {e}")
        return default
p