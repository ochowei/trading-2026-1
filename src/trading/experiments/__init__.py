"""
實驗註冊表 (Experiment Registry)
管理所有已註冊的交易實驗。
Manages all registered trading experiments.
"""

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


# === 註冊所有實驗 (Register all experiments) ===
# 新增實驗時在此加一行 import (Add one import line per new experiment)
from trading.experiments import tqqq_capitulation  # noqa: F401, E402
from trading.experiments import tqqq_cap_relaxed_entry  # noqa: F401, E402
from trading.experiments import tqqq_cap_wider_exit  # noqa: F401, E402
from trading.experiments import tqqq_cap_vix_filter  # noqa: F401, E402
