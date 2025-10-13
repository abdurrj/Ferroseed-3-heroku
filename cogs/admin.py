# cogs/admin.py
from __future__ import annotations

from typing import List
from discord.ext import commands

def _fqname(name: str) -> str:
    """
    Normalize a user-provided cog name to a fully-qualified module path.
    Accepts 'fc', 'cogs.fc', 'fc.py' etc., returns 'cogs.fc'.
    """
    n = name.strip().replace("\\", "/")
    if n.endswith(".py"):
        n = n[:-3]
    if n.startswith("cogs/"):
        n = n[5:]
    if n.startswith("cogs."):
        return n
    return f"cogs.{n}"

class Admin(commands.Cog):
    """Admin-only runtime management of cogs: load/unload/reload."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="load")
    @commands.has_permissions(administrator=True)
    async def load_cog(self, ctx: commands.Context, cog: str):
        """Load a cog (e.g. `fb!load fc`)."""
        target = _fqname(cog)
        try:
            await self.bot.load_extension(target)
            await ctx.send(f"✅ Loaded `{target}`")
        except Exception as e:
            await ctx.send(f"❌ Failed to load `{target}`: `{e}`")

    @commands.command(name="unload")
    @commands.has_permissions(administrator=True)
    async def unload_cog(self, ctx: commands.Context, cog: str):
        """Unload a cog (e.g. `fb!unload fc`)."""
        target = _fqname(cog)
        try:
            await self.bot.unload_extension(target)
            await ctx.send(f"✅ Unloaded `{target}`")
        except Exception as e:
            await ctx.send(f"❌ Failed to unload `{target}`: `{e}`")

    @commands.command(name="reload")
    @commands.has_permissions(administrator=True)
    async def reload_cog(self, ctx: commands.Context, cog: str):
        """Reload a cog (e.g. `fb!reload fc`)."""
        target = _fqname(cog)
        try:
            await self.bot.reload_extension(target)
            await ctx.send(f"🔄 Reloaded `{target}`")
        except Exception as e:
            await ctx.send(f"❌ Failed to reload `{target}`: `{e}`")

    @commands.command(name="reloadall")
    @commands.has_permissions(administrator=True)
    async def reload_all(self, ctx: commands.Context):
        """Reload all currently-loaded extensions."""
        reloaded: List[str] = []
        failed: List[str] = []
        for ext in list(self.bot.extensions.keys()):
            try:
                await self.bot.reload_extension(ext)
                reloaded.append(ext)
            except Exception as e:
                failed.append(f"{ext} ({e})")
        msg = f"🔄 Reloaded: {', '.join(reloaded) if reloaded else '—'}"
        if failed:
            msg += f"\n❌ Failed: {', '.join(failed)}"
        await ctx.send(msg)

    # Optional: nicer error if a non-admin tries these
    @load_cog.error
    @unload_cog.error
    @reload_cog.error
    @reload_all.error
    async def _perm_error(self, ctx: commands.Context, exc: Exception):
        if isinstance(exc, commands.MissingPermissions):
            await ctx.send("⛔ You need **Administrator** to use this command.")

async def setup(bot: commands.Bot):
    await bot.add_cog(Admin(bot))
