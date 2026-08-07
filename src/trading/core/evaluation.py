"""Explicit asset evaluation with fail-closed candidate refresh semantics."""

from __future__ import annotations

import math
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from datetime import UTC, date, datetime
from pathlib import Path

from trading.core.data_fetcher import create_default_market_data_service
from trading.core.results import inspect_result
from trading.experiments import get_experiment, list_experiments
from trading.market_data import (
    MarketDataBundle,
    MarketDataRequirement,
    MarketDataService,
    PrimaryUSSessionCalendar,
    SignalDecisionTime,
)
from trading.research_data import (
    ExperimentTrialDeclaration,
    ResearchDataStore,
    ResearchDefinitionSnapshot,
    ResearchRunCoordinator,
    ResultValidity,
    ResultValidityStatus,
    RunMode,
)


@dataclass(frozen=True, slots=True)
class AssetEvaluation:
    """An explicit evaluation, which is only complete when every candidate is current."""

    asset: str
    candidates: tuple[str, ...]
    refreshed: tuple[str, ...]
    ranking: tuple[str, ...]
    complete: bool
    errors: tuple[str, ...]


def canonical_ranking_score(payload: Mapping[str, object]) -> float:
    """Read the base-net Sharpe calculated from canonical daily sleeve equity."""
    evidence = payload.get("canonical_sleeve_evidence")
    if not isinstance(evidence, Mapping):
        raise RuntimeError("candidate has no canonical base-net sleeve evidence")
    scenarios = evidence.get("scenarios")
    base_net = scenarios.get("base_net") if isinstance(scenarios, Mapping) else None
    metrics = base_net.get("metrics") if isinstance(base_net, Mapping) else None
    if not isinstance(metrics, Mapping) or "sharpe_ratio" not in metrics:
        raise RuntimeError("candidate has no canonical base-net ranking metrics")
    value = metrics["sharpe_ratio"]
    if value is None:
        return float("-inf")
    try:
        score = float(value)
    except (TypeError, ValueError) as exc:
        raise RuntimeError("canonical base-net Sharpe is not numeric") from exc
    if not math.isfinite(score):
        raise RuntimeError("canonical base-net Sharpe must be finite")
    return score


def refresh_candidate_snapshot(
    experiment_name: str,
    *,
    source_manifest_path: Path,
    current_definition: ResearchDefinitionSnapshot,
    store: ResearchDataStore,
    market_data_service: MarketDataService,
    decision_session: date,
    results_root: Path,
) -> Path:
    """Fully refresh retained declarations and publish a current exact snapshot."""
    source = store.load_snapshot(source_manifest_path).manifest
    retained_requirements = tuple(
        MarketDataRequirement(
            entry.series,
            entry.history_start,
            role=entry.role,
            availability_policy=entry.availability_policy,
            coverage_policy=entry.coverage_policy,
        )
        for entry in source.data
    )
    try:
        strategy = get_experiment(experiment_name)
    except KeyError:
        strategy = None
    declaration_factory = getattr(strategy, "market_data_requirements", None)
    if callable(declaration_factory):
        declared_requirements = MarketDataBundle.validate_requirements(declaration_factory())
        if tuple(declared_requirements) != retained_requirements:
            raise RuntimeError(
                f"{experiment_name} declaration differs from retained snapshot requirements"
            )
        requirements = declared_requirements
    else:
        requirements = retained_requirements
    for requirement in requirements:
        market_data_service.refresh(
            requirement.series,
            mode="full",
            start=None,
            end=decision_session,
            coverage_policy=requirement.coverage_policy,
        )
    manifest = store.create_snapshot(
        market_data_service.cache,
        requirements,
        SignalDecisionTime.for_primary_session(decision_session),
        definition=current_definition.blob,
    )
    destination = Path(results_root) / experiment_name / f"{manifest.snapshot_id}.snapshot.json"
    return store.write_manifest(manifest, destination)


def evaluate_asset_candidates(
    asset: str,
    candidate_statuses: Mapping[str, ResultValidity],
    *,
    refresh: Callable[[str], None],
    rank_key: Callable[[str], float] | None = None,
) -> AssetEvaluation:
    """Refresh every stale candidate and suppress ranking until all are valid."""
    candidate_names = tuple(candidate_statuses)
    refreshed: list[str] = []
    errors: list[str] = []
    current: dict[str, ResultValidity] = dict(candidate_statuses)
    stale_statuses = {
        ResultValidityStatus.DATA_STALE,
        ResultValidityStatus.DEFINITION_STALE,
    }

    for name in candidate_names:
        status = current[name]
        if status.status in stale_statuses:
            refreshed.append(name)
            try:
                refresh(name)
            except Exception as exc:  # noqa: BLE001 - all candidates must be attempted
                errors.append(f"{name}: refresh failed: {exc}")
                continue
            updated = candidate_statuses.get(name)
            if isinstance(updated, ResultValidity):
                status = updated
                current[name] = updated
        if status.status is not ResultValidityStatus.VALID:
            errors.append(f"{name}: candidate is {status.status.value}")

    if not candidate_names:
        errors.append(f"{asset}: no experiment candidates were discovered")
    if errors:
        return AssetEvaluation(
            asset=asset,
            candidates=candidate_names,
            refreshed=tuple(refreshed),
            ranking=(),
            complete=False,
            errors=tuple(errors),
        )

    score = rank_key or (lambda _name: 0.0)
    try:
        ranking = tuple(sorted(candidate_names, key=lambda name: (-score(name), name)))
    except Exception as exc:  # noqa: BLE001 - ranking must fail closed
        return AssetEvaluation(
            asset=asset,
            candidates=candidate_names,
            refreshed=tuple(refreshed),
            ranking=(),
            complete=False,
            errors=(f"{asset}: ranking failed: {exc}",),
        )
    return AssetEvaluation(
        asset=asset,
        candidates=candidate_names,
        refreshed=tuple(refreshed),
        ranking=ranking,
        complete=True,
        errors=(),
    )


def evaluate_asset_from_cli(asset: str) -> None:
    """Run the explicit CLI evaluation workflow for one asset."""
    asset_upper = asset.upper()
    names: list[str] = []
    definitions: dict[str, ResearchDefinitionSnapshot] = {}
    trials: dict[str, ExperimentTrialDeclaration] = {}
    records = {}
    for name in list_experiments():
        strategy = get_experiment(name)
        config = strategy.create_config()
        if any(ticker.upper() == asset_upper for ticker in config.tickers):
            names.append(name)
            capture = getattr(strategy, "capture_research_definition", None)
            if callable(capture):
                captured = capture(_definition_store())
                if isinstance(captured, ResearchDefinitionSnapshot):
                    definitions[name] = captured
            declare_trial = getattr(strategy, "declare_experiment_trial", None)
            if callable(declare_trial):
                declared = declare_trial()
                if isinstance(declared, ExperimentTrialDeclaration):
                    trials[name] = declared

    statuses: dict[str, ResultValidity] = {}
    for name in names:
        definition = definitions.get(name)
        record = inspect_result(
            name,
            current_definition_fingerprint=definition.fingerprint if definition else None,
        )
        statuses[name] = (
            record.validity
            if record is not None
            else ResultValidity(ResultValidityStatus.UNREPRODUCIBLE, ("no latest result",))
        )
        if record is not None:
            records[name] = record

    def refresh(name: str) -> None:
        definition = definitions.get(name)
        if definition is None:
            raise RuntimeError("candidate is not snapshot-aware; legacy refresh is prohibited")
        strategy = get_experiment(name)
        runner = getattr(strategy, "run_with_bundle", None)
        if not callable(runner):
            raise RuntimeError("candidate has no snapshot-aware runner")
        trial = trials.get(name)
        if trial is None:
            raise RuntimeError("candidate has no declared experiment trial family")
        from trading.cli import create_default_research_data_store

        store = create_default_research_data_store()
        record = records.get(name)
        if record is None:
            raise RuntimeError("candidate has no retained result evidence")
        manifest = _result_manifest_path(record.path, record.result.payload)
        current_manifest = refresh_candidate_snapshot(
            name,
            source_manifest_path=manifest,
            current_definition=definition,
            store=store,
            market_data_service=create_default_market_data_service(),
            decision_session=PrimaryUSSessionCalendar().latest_completed_session(datetime.now(UTC)),
            results_root=Path("results"),
        )
        ResearchRunCoordinator(
            store=store,
            results_root=Path("results"),
            experiment_family=trial.family,
            hypothesis=trial.hypothesis,
        ).execute(
            name,
            runner,
            manifest_path=current_manifest,
            current_definition=definition.blob,
            mode=RunMode.ONLINE,
        )
        updated = inspect_result(
            name,
            current_definition_fingerprint=definition.fingerprint,
        )
        if updated is None:
            raise RuntimeError("refresh completed without a latest result")
        statuses[name] = updated.validity

    def rank_key(name: str) -> float:
        record = inspect_result(name)
        if record is None:
            raise RuntimeError("candidate result disappeared during evaluation")
        return canonical_ranking_score(record.result.payload)

    evaluation = evaluate_asset_candidates(
        asset_upper,
        statuses,
        refresh=refresh,
        rank_key=rank_key,
    )
    if not evaluation.complete:
        print(f"{asset_upper}: incomplete ranking; no candidate set was presented")
        for error in evaluation.errors:
            print(f"  error: {error}")
        raise SystemExit(1)
    print(f"{asset_upper}: complete ranking")
    for position, name in enumerate(evaluation.ranking, start=1):
        print(f"  {position}. {name}")


def _definition_store():
    from trading.cli import create_default_research_definition_store

    return create_default_research_definition_store()


def _result_manifest_path(result_path: Path, payload: Mapping[str, object]) -> Path:
    raw = payload.get("data_snapshot_manifest")
    if not isinstance(raw, str) or not raw:
        raise RuntimeError("candidate result has no data snapshot manifest")
    candidate = Path(raw)
    if candidate.is_absolute() or candidate.exists():
        return candidate
    relative = result_path.parent / candidate
    return relative if relative.exists() else candidate
