# 專案架構 (Project Structure)

```
src/trading/
├── cli.py                              # 統一 CLI 入口
├── core/                               # 共用基礎設施
│   ├── base_config.py                  # ExperimentConfig dataclass
│   ├── base_signal_detector.py         # BaseSignalDetector ABC
│   ├── base_backtester.py              # 通用回測引擎（停利/停損/到期）
│   ├── execution_backtester.py         # 成交模型回測引擎（滑價/悲觀認定/隔日開盤）
│   ├── base_strategy.py                # BaseStrategy（fetch → 指標 → 訊號 → 回測 → 報表）
│   ├── execution_strategy.py           # ExecutionModelStrategy（成交模型報表）
│   ├── data_fetcher.py                 # yfinance 多線程資料抓取
│   └── results.py                      # 結果儲存（JSON）與跨實驗比較
├── experiments/                        # 所有實驗放在這裡
│   ├── __init__.py                     # 實驗註冊表
│   ├── tqqq_capitulation/              # TQQQ 恐慌抄底策略（基礎版）
│   │   ├── config.py
│   │   ├── signal_detector.py
│   │   └── strategy.py
│   ├── tqqq_cap_relaxed_entry/         # TQQQ 放寬進場條件變體
│   │   ├── config.py
│   │   ├── signal_detector.py
│   │   └── strategy.py
│   ├── tqqq_cap_wider_exit/            # TQQQ 放寬出場條件變體
│   │   ├── backtester.py
│   │   ├── config.py
│   │   ├── signal_detector.py
│   │   └── strategy.py
│   ├── tqqq_cap_vix_filter/            # TQQQ VIX 過濾器變體
│   │   ├── config.py
│   │   ├── signal_detector.py
│   │   └── strategy.py
│   ├── tqqq_cap_vix_adaptive/          # TQQQ 軟性 VIX + 適應性出場變體
│   │   ├── config.py
│   │   ├── signal_detector.py
│   │   └── strategy.py
│   ├── tqqq_momentum_collapse/         # TQQQ 多日動能崩潰變體
│   │   ├── config.py
│   │   ├── signal_detector.py
│   │   └── strategy.py
│   ├── tqqq_cap_qqq_confirm/           # TQQQ QQQ 相對強度確認變體
│   │   ├── config.py
│   │   ├── signal_detector.py
│   │   └── strategy.py
│   ├── tqqq_cap_optimized_exit/        # TQQQ 優化出場變體（當前最佳）
│   │   ├── config.py
│   │   └── strategy.py
│   ├── tqqq_cap_gentle_entry/          # TQQQ 溫和放寬進場變體（❌ 失敗）
│   │   ├── config.py
│   │   ├── signal_detector.py
│   │   └── strategy.py
│   ├── tqqq_cap_exec_optimized/        # TQQQ 重做 008 + 成交模型（TQQQ-010）
│   │   ├── config.py
│   │   └── strategy.py
│   ├── tqqq_cap_exec_baseline/         # TQQQ 重做 001 + 成交模型（TQQQ-011）
│   │   ├── config.py
│   │   └── strategy.py
│   ├── tqqq_cap_exec_qqq_confirm/      # TQQQ 重做 007 + 成交模型（TQQQ-012）
│   │   ├── config.py
│   │   └── strategy.py
│   ├── tqqq_cap_exec_qqq_optimized/    # TQQQ QQQ 確認 + 優化出場 + 成交模型（TQQQ-013，失敗）
│   │   ├── config.py
│   │   └── strategy.py
│   └── _template/                      # 新實驗模板（複製即用）
│       ├── __init__.py
│       ├── config.py
│       ├── signal_detector.py
│       └── strategy.py
```
