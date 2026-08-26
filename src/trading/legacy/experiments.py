"""Registry implementation for the frozen legacy experiment inventory."""

import importlib
import pkgutil
from collections.abc import Iterable

from trading.core.base_strategy import BaseStrategy

_REGISTRY: dict[str, type[BaseStrategy]] = {}


def register(name: str):
    """Register one archived experiment class under its historical identity."""

    def wrapper(cls: type[BaseStrategy]) -> type[BaseStrategy]:
        _REGISTRY[name] = cls
        return cls

    return wrapper


def get_experiment(name: str) -> BaseStrategy:
    """Instantiate one registered archived experiment."""
    if name not in _REGISTRY:
        available = ", ".join(sorted(_REGISTRY))
        raise KeyError(
            f"找不到實驗 '{name}' (Experiment '{name}' not found). "
            f"可用的實驗 (Available): {available}"
        )
    return _REGISTRY[name]()


def list_experiments() -> list[str]:
    """List every registered archived experiment identity."""
    return sorted(_REGISTRY)


def discover(package_name: str, package_paths: Iterable[str]) -> None:
    """Import archived packages through the historical package namespace."""
    for _finder, module_name, _is_package in pkgutil.iter_modules(package_paths):
        if not module_name.startswith("_"):
            importlib.import_module(f"{package_name}.{module_name}")
