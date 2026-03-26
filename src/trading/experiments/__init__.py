"""
實驗註冊表 (Experiment Registry)
管理所有已註冊的交易實驗。
Manages all registered trading experiments.
"""

import importlib
import pkgutil

from trading.core.base_strategy import BaseStrategy

_REGISTRY: dict[str, type[BaseStrategy]] = {}


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


# === 自動發現並註冊所有實驗 (Auto-discover and register all experiments) ===
# 每個實驗的 __init__.py 會呼叫 register() 完成註冊
# 新增實驗時不需要修改此檔案
for _finder, _module_name, _ispkg in pkgutil.iter_modules(__path__):
    if not _module_name.startswith("_"):
        importlib.import_module(f"{__name__}.{_module_name}")
