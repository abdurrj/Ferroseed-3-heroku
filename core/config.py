# core/config.py
import os
from typing import Any, Dict, List
import yaml  # pip install pyyaml

def _sub_env(val: Any) -> Any:
    if isinstance(val, str) and val.startswith("${") and val.endswith("}"):
        key = val[2:-1]
        return os.getenv(key, val)  # if missing, keep the placeholder
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
    def modules(self) -> List[str]:
        mods: List[str] = []
        for name, cfg in (self.data.get("modules") or {}).items():
            if isinstance(cfg, dict) and cfg.get("enabled"):
                mods.append(name)
            elif isinstance(cfg, bool) and cfg:
                mods.append(name)
        return mods

CONFIG = Config()
