"""TLT HYG Credit Divergence Regime-Gated MR (TLT-015)"""

from trading.experiments import register
from trading.experiments.tlt_015_hyg_credit_divergence_mr.strategy import (
    TLT015HygCreditDivergenceMRStrategy,
)

register("tlt_015_hyg_credit_divergence_mr")(TLT015HygCreditDivergenceMRStrategy)
