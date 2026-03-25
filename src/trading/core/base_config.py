"""
實驗配置基礎類別 (Base Experiment Configuration)
所有實驗的配置都繼承此 dataclass。
All experiment configs inherit from this dataclass.
"""

from dataclasses import dataclass, field


@dataclass
class ExperimentConfig:
    """實驗配置基礎類別 (Base config every experiment must provide)"""

    # 實驗識別 (Experiment identity)
    name: str                          # e.g. "tqqq_capitulation"
    experiment_id: str = ""            # e.g. "TQQQ-001"
    display_name: str = ""             # e.g. "TQQQ Capitulation Buy"

    # 標的與資料 (Tickers and data)
    tickers: list[str] = field(default_factory=lambda: [])
    data_start: str = "2019-01-01"     # 最早需要的資料日期

    # 回測區間 Part A/B/C (Backtest date ranges)
    part_a_start: str = "2019-01-01"
    part_a_end: str = "2023-12-31"
    part_b_start: str = "2024-01-01"
    part_b_end: str = "2025-12-31"
    part_c_start: str = "2026-01-01"
    part_c_end: str = ""               # 空字串表示至今 (empty = up to today)

    # 預設出場參數 (Default exit parameters)
    profit_target: float = 0.05        # +5%
    stop_loss: float = -0.08           # -8%
    holding_days: int = 7              # 最長持倉天數

    def get_parts(self) -> list[tuple[str, str, str]]:
        """回傳 Part A/B/C 區間列表 (Return list of (label, start, end) tuples)"""
        return [
            ("Part A (In-Sample)", self.part_a_start, self.part_a_end),
            ("Part B (Out-of-Sample)", self.part_b_start, self.part_b_end),
            ("Part C (Live)", self.part_c_start, self.part_c_end),
        ]
