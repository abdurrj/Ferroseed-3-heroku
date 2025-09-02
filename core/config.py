# core/config.py
import os
from typing import Any, Dict, List
import yaml  # pip install pyyaml

def _sub_env(val: Any) -> Any:
    if isinstance(val, str) and val.startswith("${") and val.endswith("}"):
        key = val[2:-1]
        return os.getenv(key, val)  # keep placeholder if missing
    return val

def _apply_env(obj: Any) -> Any:
    if isinstance(obj, dict):
        return {k: _apply_env(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_apply_env(v) for v in obj]
    return _sub_env(obj)

class Config:
    def __init__(self, path: str = "application.yml"):
        with open(path, "r", encoding="utf-8") as f:
            raw: Dict[str, Any] = yaml.safe_load(f) or {}
        self.data = _apply_env(raw)

    @property
    def token(self) -> str:
        return self.data["bot"]["token"]

    @property
    def database_url(self) -> str:
        return self.data["database"]["url"]

    @property
    def default_prefix(self) -> str:
        return self.data["bot"].get("defaultPrefix", "fb!")

    @property
    def enabled_cogs(self) -> List[str]:
        """
        Reads extensions.cogs and returns only those with enabled: true.
        Supports both {name: {enabled: true}} and {name: true}.
        """
        ext = self.data.get("extensions") or {}
        mapping = ext.get("cogs") or {}
        result: List[str] = []
        if isinstance(mapping, dict):
            for name, val in mapping.items():
                if (isinstance(val, dict) and val.get("enabled")) or (isinstance(val, bool) and val):
                    result.append(str(name))
        return result

CONFIG = Config()
