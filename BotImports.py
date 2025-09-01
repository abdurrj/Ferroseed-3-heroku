import os
import json
from discord.ext import commands
from dotenv import load_dotenv

# Optional YAML support for nicer config (pip install pyyaml).
try:
    import yaml  # type: ignore
except Exception:
    yaml = None

load_dotenv()

# ---------------- Paths ----------------
ballListJson = 'data/ball_list.json'          # kept for compatibility
MODULES_YML   = 'application.yml'              # new preferred place
MODULES_JSON  = 'data/ext_modules.json'        # legacy fallback

# ---------------- Secrets / Config ----------------
def _read_first_line(path: str) -> str | None:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.readline().strip()
    except FileNotFoundError:
        return None

# Prefer env; fallback to local files (keeps dev simple).
TOKEN = os.getenv("TOKEN") or _read_first_line("token.txt")
DATABASE_URL = os.getenv("DATABASE_URL") or _read_first_line("database_url.txt")

if not TOKEN:
    raise RuntimeError("TOKEN not set (env TOKEN or token.txt required)")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL not set (env DATABASE_URL or database_url.txt required)")

defaultPrefix = "fb!"

# ---------------- Prefix helpers ----------------
async def getPrefix(client, message):
    """
    Dynamic per-guild prefix. Creates a default row if missing.
    Requires table: ferroseed.guilds(guild_id BIGINT PRIMARY KEY, prefix TEXT)
    """
    if not getattr(message, "guild", None):
        return commands.when_mentioned_or(defaultPrefix)(client, message)

    # asyncpg pool attached as client.db
    row = await client.db.fetchrow(
        'SELECT prefix FROM ferroseed.guilds WHERE guild_id = $1',
        message.guild.id
    )
    if not row:
        await client.db.execute(
            'INSERT INTO ferroseed.guilds(guild_id, prefix) VALUES ($1, $2)',
            message.guild.id, defaultPrefix
        )
        return defaultPrefix
    return row["prefix"]

async def setPrefix(client, message, prefix: str):
    await client.db.execute(
        'UPDATE ferroseed.guilds SET prefix=$1 WHERE guild_id=$2',
        prefix, message.guild.id
    )

# ---------------- Modules config (file-based) ----------------
def _load_modules_from_yaml(path: str) -> list[str]:
    if not yaml:
        return []
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    mods = []
    for name, cfg in (data.get("modules") or {}).items():
        if isinstance(cfg, dict) and cfg.get("enabled"):
            mods.append(name)
        elif isinstance(cfg, bool) and cfg:  # allow simple true/false
            mods.append(name)
    return mods

def _load_modules_from_json(path: str) -> list[str]:
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    # Accept ["fc","raid"] or {"fc": true, "raid": false}
    if isinstance(data, list):
        return [str(x) for x in data]
    if isinstance(data, dict):
        return [k for k, v in data.items() if v]
    return []

async def getExternalModules(client=None) -> list[str]:
    """
    Replacement for old DB-backed modules list.
    Priority:
      1) application.yml (YAML)
      2) data/ext_modules.json (legacy)
    """
    mods = _load_modules_from_yaml(MODULES_YML)
    if mods:
        return mods
    # Legacy fallback
    return _load_modules_from_json(MODULES_JSON)

# Keeping the write function for compatibility; now writes to file.
async def writeExternalModules(client, data):
    """
    Writes enabled modules to application.yml if YAML is available,
    otherwise to data/ext_modules.json as a simple list.
    """
    data = list(dict.fromkeys(map(str, data)))  # de-duplicate, keep order
    if yaml:
        doc = {"modules": {name: {"enabled": True} for name in data}}
        os.makedirs(os.path.dirname(MODULES_YML) or ".", exist_ok=True)
        with open(MODULES_YML, "w", encoding="utf-8") as f:
            yaml.safe_dump(doc, f, sort_keys=True, allow_unicode=True)
    else:
        os.makedirs(os.path.dirname(MODULES_JSON) or ".", exist_ok=True)
        with open(MODULES_JSON, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

# ---------------- Tiny JSON helpers (unchanged) ----------------
def getJson(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def writeJson(path, data):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
