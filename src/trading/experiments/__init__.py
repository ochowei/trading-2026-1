"""
實驗註冊表 (Experiment Registry)
管理所有已註冊的 legacy 交易實驗。
Manages the closed inventory of registered legacy trading experiments.
"""

import importlib
import pkgutil
from pathlib import Path

from trading.core.base_strategy import BaseStrategy

_REGISTRY: dict[str, type[BaseStrategy]] = {}

# Keep the historical import identity ``trading.experiments.<name>`` stable while
# storing the closed legacy packages in a clearly separated archive directory.
_LEGACY_PACKAGE_PATH = Path(__file__).resolve().parents[3] / "legacy" / "experiments"
__path__.append(str(_LEGACY_PACKAGE_PATH))


def register(name: str):
    """
    註冊實驗的裝飾器 (Decorator to register an experiment)

    Usage:
        @register("my_experiment")
        class MyStrategy(BaseStrategy):
            ...
    """

    def wrapper(cls: type[BaseStrategy]) -> type[BaseStrategy]:
        _REGISTRY[name] = cls
        return cls

    return wrapper


def get_experiment(name: str) -> BaseStrategy:
    """取得實驗實例 (Get an experiment instance by name)"""
    if name not in _REGISTRY:
        available = ", ".join(sorted(_REGISTRY.keys()))
        raise KeyError(
            f"找不到實驗 '{name}' (Experiment '{name}' not found). "
            f"可用的實驗 (Available): {available}"
        )
    return _REGISTRY[name]()


def list_experiments() -> list[str]:
    """列出所有已註冊的實驗 (List all registered experiments)"""
    return sorted(_REGISTRY.keys())


# === 自動發現並註冊既有 legacy 實驗 (Auto-discover registered legacy experiments) ===
# 每個實驗的 __init__.py 會呼叫 register() 完成註冊
# 新研究不得新增 package；使用 trading.research_definitions registry。
for _finder, _module_name, _ispkg in pkgutil.iter_modules(__path__):
    if not _module_name.startswith("_"):
        importlib.import_module(f"{__name__}.{_module_name}")
