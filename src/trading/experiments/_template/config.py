"""
<實驗名稱> 配置 (<Experiment Name> Configuration)
定義此實驗的所有參數與閾值。
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class MyConfig(ExperimentConfig):
    """自訂實驗配置 (Custom experiment config)"""

    # 在此新增策略專屬參數 (Add strategy-specific parameters here)
    # example_param: float = 0.5
    pass


def create_default_config() -> MyConfig:
    """建立預設配置 (Create default config)"""
    return MyConfig(
        name="my_experiment",                    # 實驗 ID
        display_name="My Experiment",            # 顯示名稱
        tickers=["SPY"],                         # 標的
        data_start="2019-01-01",                 # 資料起始日
        profit_target=0.05,                      # 獲利目標
        stop_loss=-0.08,                         # 停損
        holding_days=7,                          # 最長持倉
    )
