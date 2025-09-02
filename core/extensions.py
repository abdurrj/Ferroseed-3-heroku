# core/extensions.py
from typing import Iterable, List, Optional
from core.config import CONFIG
from core.prefix import get_prefix

async def load_all_extensions(bot, base: Optional[Iterable[str]] = None) -> None:
    bot.command_prefix = get_prefix

    # Always-on cogs you own
    base_list: List[str] = list(base) if base is not None else [
        "cogs.events",
        "cogs.ping",
    ]

    # Enabled cogs from application.yml
    dynamic = [f"cogs.{name}" for name in CONFIG.enabled_cogs]

    to_load = base_list + dynamic
    loaded, failed = [], []
    for name in to_load:
        try:
            await bot.load_extension(name)
            loaded.append(name)
        except Exception as e:
            print(f"[ext] Failed to load {name}: {e}")
            failed.append(name)

    print("[ext] Loaded :", ", ".join(loaded) if loaded else "—")
    print("[ext] Failed :", ", ".join(failed) if failed else "—")
