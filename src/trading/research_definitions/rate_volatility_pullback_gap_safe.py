"""Rate-volatility pullbacks that suppress signals when auxiliary data is over-age."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path

import pandas as pd

import trading.research_definitions.rate_volatility_pullback as base_runtime
from trading.core.sleeve_engine import CANONICAL_SLEEVE_ENGINE_VERSION, CanonicalSleeveInput
from trading.market_data import (
    MarketDataBundle,
    MarketDataCoveragePolicy,
    MarketDataRequirement,
    MarketDataSeries,
)
from trading.market_data.availability import GapAwareAvailabilityPolicy
from trading.policies import PolicySet
from trading.research_data import ResearchDefinitionSnapshot, ResearchDefinitionStore
from trading.research_definitions.daily_bar import execution_cost_policies
from trading.research_definitions.rate_volatility_pullback import (
    RateVolatilityPullbackResearchDefinition,
    build_rate_volatility_candidates,
)


@dataclass(frozen=True, slots=True)
class GapSafeRateVolatilityPullbackResearchDefinition(RateVolatilityPullbackResearchDefinition):
    """A permanent definition that makes over-age auxiliary decisions non-signaling."""

    def market_data_requirements(self) -> tuple[MarketDataRequirement, ...]:
        primary = MarketDataRequirement(
            MarketDataSeries.yahoo_adjusted_daily(self.config.ticker),
            self.config.history_start,
            role="primary",
        )
        if self.config.move_ticker is None:
            return (primary,)
        return (
            primary,
            MarketDataRequirement(
                MarketDataSeries.yahoo_adjusted_daily(self.config.move_ticker),
                self.config.history_start,
                role="auxiliary",
                availability_policy=GapAwareAvailabilityPolicy(
                    publication_lag_sessions=1,
                    max_observation_lag_sessions=self.config.auxiliary_max_lag_sessions,
                    publication_time_known=False,
                ),
                coverage_policy=MarketDataCoveragePolicy.provider_observations(),
            ),
        )

    def capture_research_definition(
        self, store: ResearchDefinitionStore, policy_set: PolicySet
    ) -> ResearchDefinitionSnapshot:
        market_release = next(
            (
                release
                for release in policy_set.releases
                if release.identity.family == "us-equity-market"
            ),
            None,
        )
        if (
            market_release is None
            or market_release.identity.version != "v002"
            or "mark_unavailable"
            not in market_release.values.get("allowed_excess_observation_lag_modes", ())
            or market_release.values.get("mark_unavailable_requires_signal_suppression") is not True
            or market_release.values.get("mark_unavailable_requires_manifest_evidence") is not True
        ):
            raise ValueError(
                "gap-safe definitions require us-equity-market@v002 with explicit "
                "mark_unavailable controls"
            )
        base, stress = execution_cost_policies(policy_set)
        return store.capture(
            resolved_config={
                "identity": self.identity,
                "config": asdict(self.config),
                "market_data_requirements": self.market_data_requirements(),
            },
            sources={
                "strategy": self.source_path.resolve(),
                "detector": Path(base_runtime.__file__).resolve(),
                "backtester": Path(__file__).resolve(),
            },
            execution_engine_version=CANONICAL_SLEEVE_ENGINE_VERSION,
            dependency_versions={"pandas": pd.__version__},
            base_cost_policy=base,
            stress_cost_policy=stress,
            policy_set=policy_set,
            workflow_native=True,
        )

    def run_with_bundle(self, bundle: MarketDataBundle) -> dict[str, object]:
        requirements = self.market_data_requirements()
        if tuple(bundle) != tuple(item.series for item in requirements):
            raise ValueError("bundle keys do not match the frozen data declaration")
        primary = bundle[requirements[0].series]
        auxiliary = bundle[requirements[1].series] if len(requirements) == 2 else None
        research = primary.loc[pd.Timestamp(self.config.research_start) :]
        candidates, signals = build_rate_volatility_candidates(primary, auxiliary, self.config)
        if auxiliary is not None:
            if "ObservationAvailable" not in auxiliary.columns:
                raise ValueError("gap-safe MOVE observations lack availability decisions")
            available = auxiliary["ObservationAvailable"]
            candidates = tuple(
                candidate
                for candidate in candidates
                if bool(available.loc[pd.Timestamp(candidate.signal_date)])
            )
            signals = tuple(
                signal for signal in signals if bool(available.loc[pd.Timestamp(signal)])
            )
        return {
            "metadata": {
                "research_definition": self.identity,
                "ticker": self.config.ticker,
                "auxiliary_ticker": self.config.move_ticker,
                "data_cutoff": primary.index[-1].date().isoformat(),
            },
            "canonical_sleeve_input": CanonicalSleeveInput(
                calendar=tuple(research.index),
                close_prices=research["Close"].copy(deep=True),
                candidates=candidates,
                raw_signals=signals,
                legacy_signals=signals,
                legacy_candidates=candidates,
                initial_capital=1.0,
            ),
        }
