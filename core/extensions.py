# core/extensions.py
from typing import Iterable, List, Optional

from core.config import CONFIG
try:
    # If you've created core/prefix.py with get_prefix:
    from core.prefix import get_prefix  # noqa: F401
    _HAS_PREFIX = True
except Exception:
    _HAS_PREFIX = False


async def load_all_extensions(bot, base: Optional[Iterable[str]] = None) -> None:
    """
    Loads base cogs plus dynamic modules listed in application.yml (CONFIG.modules).
    - Sets the bot's dynamic command prefix if core.prefix.get_prefix exists.
    - Prints a short summary of loaded / failed extensions.
    """
    if _HAS_PREFIX:
        bot.command_prefix = get_prefix  # dynamic per-guild prefix

    # Base cogs you always want (adjust as you add more)
    base_list: List[str] = list(base) if base is not None else ["cogs.events", "cogs.ping"]

    # Dynamic modules from config (e.g., modules.fc.enabled: true)
    dynamic = [f"modules.{name}" for name in CONFIG.modules]

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
