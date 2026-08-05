from datetime import UTC, datetime

import pandas as pd
import pytest

from trading.core.followup_cutover import (
    DataAccessParityCorrection,
    DataAccessParityOutputs,
    FollowupActivationProof,
    FollowupActivationVerifier,
    FollowupAuthorizationContext,
    FollowupLifecycleRegistry,
    FollowupShadowProof,
    FollowupStrategy,
    StrategyLifecycle,
    authorize_followup_order,
    build_followup_status_report,
    evaluate_data_access_parity,
    run_verified_data_access_parity,
)


def _strategy(
    ticker: str = "SPY",
    experiment_name: str = "spy_007_trend_pullback",
) -> FollowupStrategy:
    return FollowupStrategy(ticker=ticker, experiment_name=experiment_name)


def _shadow_proof(shadow_id: str = "shadow-1") -> FollowupShadowProof:
    return FollowupShadowProof(
        shadow_id=shadow_id,
        registration_event_id=f"shadow-registration:{shadow_id}",
        historical_screen_event_id="historical-screen:plan-1",
        result_fingerprint="a" * 64,
        parity_digest="b" * 64,
    )


def _buy_context(**overrides: object) -> FollowupAuthorizationContext:
    values: dict[str, object] = {
        "lifecycle": StrategyLifecycle.ACTIVE,
        "no_new_entry": False,
        "result_valid": True,
        "result_identity": "result-spy-007-snapshot-1",
        "active_proof_current": True,
        "data_fresh": True,
        "data_cutoff": "2026-08-05",
        "data_bundle_identity": "b" * 64,
        "ledger_verified": True,
        "ledger_accounting_hash": "a" * 64,
        "broker_reconciled": True,
        "proposal_epoch_current": True,
        "has_actual_position": False,
    }
    values.update(overrides)
    return FollowupAuthorizationContext(**values)  # type: ignore[arg-type]


@pytest.mark.parametrize(
    ("overrides", "reason"),
    [
        ({"lifecycle": StrategyLifecycle.LEGACY_ACTIVE}, "strategy is legacy_active"),
        ({"lifecycle": StrategyLifecycle.RETIRING}, "strategy is retiring"),
        ({"lifecycle": StrategyLifecycle.SHADOW}, "strategy is shadow"),
        ({"lifecycle": StrategyLifecycle.PAUSED}, "strategy is paused"),
        ({"no_new_entry": True}, "no-new-entry mode is enabled"),
        ({"result_valid": False}, "research result is not valid"),
        ({"result_identity": ""}, "valid result identity is missing"),
        (
            {"active_proof_current": False},
            "Active proof does not match the current result",
        ),
        ({"data_fresh": False}, "market data is stale"),
        ({"data_cutoff": ""}, "market data cutoff is missing"),
        ({"data_bundle_identity": ""}, "market data bundle identity is missing"),
        ({"ledger_verified": False}, "ledger is not verified"),
        ({"ledger_accounting_hash": ""}, "ledger accounting identity is missing"),
        ({"broker_reconciled": False}, "broker reconciliation is not current"),
        ({"proposal_epoch_current": False}, "proposal allocation epoch is not current"),
        ({"has_actual_position": True}, "strategy sleeve already has an actual position"),
    ],
)
def test_buy_authorization_fails_closed_for_every_phase_7_guard(
    overrides: dict[str, object],
    reason: str,
) -> None:
    decision = authorize_followup_order("BUY", _buy_context(**overrides))

    assert decision.authorized is False
    assert decision.reason == reason


def test_buy_authorization_requires_all_phase_7_guards() -> None:
    decision = authorize_followup_order("BUY", _buy_context())

    assert decision.authorized is True
    assert decision.reason == "authorized"


@pytest.mark.parametrize(
    "lifecycle",
    [
        StrategyLifecycle.LEGACY_ACTIVE,
        StrategyLifecycle.RETIRING,
        StrategyLifecycle.PAUSED,
        StrategyLifecycle.ACTIVE,
    ],
)
def test_verified_actual_position_can_be_managed_to_exit(lifecycle: StrategyLifecycle) -> None:
    decision = authorize_followup_order(
        "SELL",
        _buy_context(
            lifecycle=lifecycle,
            no_new_entry=True,
            result_valid=False,
            data_fresh=False,
            broker_reconciled=False,
            has_actual_position=True,
        ),
    )

    assert decision.authorized is True
    assert decision.reason == "verified actual-position exit"


def test_exit_requires_verified_ledger_position() -> None:
    missing_position = authorize_followup_order(
        "SELL",
        _buy_context(has_actual_position=False),
    )
    unverified = authorize_followup_order(
        "SELL",
        _buy_context(has_actual_position=True, ledger_verified=False),
    )

    assert missing_position.reason == "no actual position exists"
    assert unverified.reason == "ledger is not verified"


def test_cutover_initialization_marks_followup_legacy_and_pauses_entries(tmp_path) -> None:
    registry = FollowupLifecycleRegistry(tmp_path / "followup-lifecycle.json")
    strategies = (_strategy(), _strategy("QQQ", "qqq_001_fixture"))
    occurred_at = datetime(2026, 8, 6, 12, 0, tzinfo=UTC)

    state = registry.initialize_cutover(strategies, occurred_at=occurred_at)

    assert state.no_new_entry is True
    assert state.status_for("SPY", "spy_007_trend_pullback") is StrategyLifecycle.LEGACY_ACTIVE
    assert state.status_for("QQQ", "qqq_001_fixture") is StrategyLifecycle.LEGACY_ACTIVE
    assert registry.initialize_cutover(strategies, occurred_at=occurred_at) == state


def test_cutover_initialization_conflicts_instead_of_rewriting_history(tmp_path) -> None:
    registry = FollowupLifecycleRegistry(tmp_path / "followup-lifecycle.json")
    occurred_at = datetime(2026, 8, 6, 12, 0, tzinfo=UTC)
    registry.initialize_cutover((_strategy(),), occurred_at=occurred_at)

    with pytest.raises(ValueError, match="cutover initialization conflicts"):
        registry.initialize_cutover(
            (_strategy("QQQ", "qqq_001_fixture"),),
            occurred_at=occurred_at,
        )


def test_registry_enforces_one_active_strategy_per_ticker(tmp_path) -> None:
    registry = FollowupLifecycleRegistry(
        tmp_path / "followup-lifecycle.json",
        activation_verifier=lambda _strategy, _proof: None,
        shadow_verifier=lambda _strategy, _proof: None,
    )
    occurred_at = datetime(2026, 8, 6, 12, 0, tzinfo=UTC)
    first = _strategy()
    replacement = _strategy("SPY", "spy_008_replacement")
    registry.initialize_cutover((first,), occurred_at=occurred_at)
    registry.register_shadow_strategy(
        replacement,
        proof=_shadow_proof("shadow-spy-008"),
        occurred_at=datetime(2026, 8, 7, 12, 0, tzinfo=UTC),
        reason="historical screen passed",
    )
    registry.register_shadow_strategy(
        first,
        proof=_shadow_proof("shadow-spy-007"),
        occurred_at=datetime(2026, 8, 7, 13, 0, tzinfo=UTC),
        reason="historical screen passed",
    )
    registry.activate_strategy(
        first,
        proof=FollowupActivationProof(
            shadow_id="shadow-spy-007",
            qualification_event_id="activation-evaluation:shadow-spy-007:2027-08-08",
            result_fingerprint="a" * 64,
            parity_digest="b" * 64,
        ),
        occurred_at=datetime(2026, 8, 8, 12, 0, tzinfo=UTC),
        reason="prospective qualification passed",
    )

    with pytest.raises(ValueError, match="already has an Active Strategy"):
        registry.activate_strategy(
            replacement,
            proof=FollowupActivationProof(
                shadow_id="shadow-spy-008",
                qualification_event_id="activation-evaluation:shadow-spy-008:2027-08-09",
                result_fingerprint="c" * 64,
                parity_digest="d" * 64,
            ),
            occurred_at=datetime(2026, 8, 9, 12, 0, tzinfo=UTC),
            reason="prospective qualification passed",
        )


def test_active_transition_requires_verified_qualification_proof(tmp_path) -> None:
    strategy = _strategy()
    unverified = FollowupLifecycleRegistry(
        tmp_path / "unverified.json",
        shadow_verifier=lambda _strategy, _proof: None,
    )
    unverified.initialize_cutover(
        (strategy,),
        occurred_at=datetime(2026, 8, 6, 12, 0, tzinfo=UTC),
    )

    with pytest.raises(ValueError, match="activate_strategy"):
        unverified.transition(
            strategy,
            lifecycle=StrategyLifecycle.ACTIVE,
            occurred_at=datetime(2026, 8, 7, 12, 0, tzinfo=UTC),
            reason="caller says eligible",
        )
    with pytest.raises(ValueError, match="activate_strategy"):
        unverified.register_strategy(
            _strategy("QQQ", "qqq_001_fixture"),
            lifecycle=StrategyLifecycle.ACTIVE,
            occurred_at=datetime(2026, 8, 7, 12, 30, tzinfo=UTC),
            reason="caller says eligible",
        )
    unverified.register_shadow_strategy(
        strategy,
        proof=_shadow_proof(),
        occurred_at=datetime(2026, 8, 7, 13, 0, tzinfo=UTC),
        reason="historical screen passed",
    )
    with pytest.raises(ValueError, match="activation verifier"):
        unverified.activate_strategy(
            strategy,
            proof=FollowupActivationProof(
                shadow_id="shadow-1",
                qualification_event_id="activation-evaluation:shadow-1:2027-08-07",
                result_fingerprint="a" * 64,
                parity_digest="b" * 64,
            ),
            occurred_at=datetime(2026, 8, 7, 12, 0, tzinfo=UTC),
            reason="caller says eligible",
        )


def test_activation_rechecks_shadow_state_after_proof_verification(tmp_path) -> None:
    strategy = _strategy()
    path = tmp_path / "lifecycle.json"
    registry: FollowupLifecycleRegistry

    def verifier(_strategy, _proof):
        registry.transition(
            strategy,
            lifecycle=StrategyLifecycle.PAUSED,
            occurred_at=datetime(2027, 8, 8, 11, 0, tzinfo=UTC),
            reason="concurrent operator pause",
        )

    registry = FollowupLifecycleRegistry(
        path,
        activation_verifier=verifier,
        shadow_verifier=lambda _strategy, _proof: None,
    )
    registry.initialize_cutover((strategy,), occurred_at=datetime(2026, 8, 6, 12, 0, tzinfo=UTC))
    registry.register_shadow_strategy(
        strategy,
        proof=_shadow_proof(),
        occurred_at=datetime(2026, 8, 7, 12, 0, tzinfo=UTC),
        reason="verified Shadow",
    )

    with pytest.raises(ValueError, match="only a registered Shadow"):
        registry.activate_strategy(
            strategy,
            proof=FollowupActivationProof(
                shadow_id="shadow-1",
                qualification_event_id="activation-evaluation:shadow-1:2027-08-08",
                result_fingerprint="a" * 64,
                parity_digest="b" * 64,
            ),
            occurred_at=datetime(2027, 8, 8, 12, 0, tzinfo=UTC),
            reason="prospective qualification passed",
        )


def test_active_strategy_requires_explicit_retirement_and_stays_retiring_until_flat(
    tmp_path,
) -> None:
    strategy = _strategy()
    positions = {strategy: True}
    registry = FollowupLifecycleRegistry(
        tmp_path / "followup-lifecycle.json",
        activation_verifier=lambda _strategy, _proof: None,
        actual_position_resolver=lambda item: positions.get(item, False),
        outstanding_entry_resolver=lambda _item: False,
        shadow_verifier=lambda _strategy, _proof: None,
    )
    registry.initialize_cutover(
        (strategy,),
        occurred_at=datetime(2026, 8, 6, 12, 0, tzinfo=UTC),
    )
    registry.register_shadow_strategy(
        strategy,
        proof=_shadow_proof("shadow-spy-007"),
        occurred_at=datetime(2026, 8, 7, 12, 0, tzinfo=UTC),
        reason="historical screen passed",
    )
    registry.activate_strategy(
        strategy,
        proof=FollowupActivationProof(
            shadow_id="shadow-spy-007",
            qualification_event_id="activation-evaluation:shadow-spy-007:2027-08-08",
            result_fingerprint="a" * 64,
            parity_digest="b" * 64,
        ),
        occurred_at=datetime(2027, 8, 8, 12, 0, tzinfo=UTC),
        reason="prospective qualification passed",
    )

    with pytest.raises(ValueError, match="retire_strategy"):
        registry.transition(
            strategy,
            lifecycle=StrategyLifecycle.PAUSED,
            occurred_at=datetime(2027, 8, 9, 12, 0, tzinfo=UTC),
            reason="replacement selected",
        )

    retiring = registry.retire_strategy(
        strategy,
        occurred_at=datetime(2027, 8, 9, 12, 0, tzinfo=UTC),
        reason="replacement selected",
    )
    assert retiring.status_for(strategy.ticker, strategy.experiment_name) is (
        StrategyLifecycle.RETIRING
    )

    with pytest.raises(ValueError, match="actual position is flat"):
        registry.complete_retirement(
            strategy,
            occurred_at=datetime(2027, 8, 10, 12, 0, tzinfo=UTC),
            reason="operator claims flat",
        )

    positions[strategy] = False
    retired = registry.complete_retirement(
        strategy,
        occurred_at=datetime(2027, 8, 11, 12, 0, tzinfo=UTC),
        reason="verified ledger position is flat",
    )
    assert retired.status_for(strategy.ticker, strategy.experiment_name) is (
        StrategyLifecycle.PAUSED
    )


def test_registry_can_roll_back_to_no_new_entry_without_losing_lifecycle(tmp_path) -> None:
    registry = FollowupLifecycleRegistry(tmp_path / "followup-lifecycle.json")
    strategy = _strategy()
    registry.initialize_cutover(
        (strategy,),
        occurred_at=datetime(2026, 8, 6, 12, 0, tzinfo=UTC),
    )
    registry.set_no_new_entry(
        False,
        occurred_at=datetime(2026, 8, 7, 12, 0, tzinfo=UTC),
        reason="controlled activation",
    )
    rolled_back = registry.set_no_new_entry(
        True,
        occurred_at=datetime(2026, 8, 8, 12, 0, tzinfo=UTC),
        reason="operator rollback",
    )

    assert rolled_back.no_new_entry is True
    assert rolled_back.status_for(strategy.ticker, strategy.experiment_name) is (
        StrategyLifecycle.LEGACY_ACTIVE
    )
    assert len(rolled_back.events) == 3


def test_registry_detects_rewritten_or_truncated_history(tmp_path) -> None:
    path = tmp_path / "followup-lifecycle.json"
    registry = FollowupLifecycleRegistry(path)
    registry.initialize_cutover(
        (_strategy(),),
        occurred_at=datetime(2026, 8, 6, 12, 0, tzinfo=UTC),
    )
    original = path.read_text(encoding="utf-8")
    path.write_text(original.replace("legacy_active", "active"), encoding="utf-8")

    with pytest.raises(ValueError, match="integrity"):
        registry.read()


def test_data_access_migration_requires_indicator_signal_and_trade_parity() -> None:
    index = pd.to_datetime(["2026-08-03", "2026-08-04"])
    indicators = pd.DataFrame({"Close": [100.0, 101.0], "RSI": [40.0, 45.0]}, index=index)
    trades = (
        {
            "signal_date": "2026-08-03",
            "entry_date": "2026-08-04",
            "entry_price": "101",
        },
    )

    result = evaluate_data_access_parity(
        legacy_indicators=indicators,
        migrated_indicators=indicators.copy(),
        legacy_signals=(index[0].date(),),
        migrated_signals=(index[0].date(),),
        legacy_trades=trades,
        migrated_trades=trades,
    )

    assert result.passed is True
    assert result.differences == ()


def test_unclassified_data_access_difference_blocks_migration() -> None:
    index = pd.to_datetime(["2026-08-03", "2026-08-04"])
    legacy = pd.DataFrame({"RSI": [40.0, 45.0]}, index=index)
    migrated = pd.DataFrame({"RSI": [40.0, 46.0]}, index=index)

    result = evaluate_data_access_parity(
        legacy_indicators=legacy,
        migrated_indicators=migrated,
        legacy_signals=(index[0].date(),),
        migrated_signals=(index[1].date(),),
        legacy_trades=(),
        migrated_trades=(),
    )

    assert result.passed is False
    assert {difference.scope for difference in result.differences} == {"indicator", "signal"}
    assert all(difference.classification == "unclassified" for difference in result.differences)


def test_production_activation_verifies_parity_shadow_and_current_result(tmp_path) -> None:
    path = tmp_path / "followup-lifecycle.json"
    strategy = _strategy()
    reader = FollowupLifecycleRegistry(
        path,
        shadow_verifier=lambda _strategy, _proof: None,
    )
    reader.initialize_cutover(
        (strategy,),
        occurred_at=datetime(2026, 8, 6, 12, 0, tzinfo=UTC),
    )
    reader.register_shadow_strategy(
        strategy,
        proof=_shadow_proof(),
        occurred_at=datetime(2026, 8, 7, 12, 0, tzinfo=UTC),
        reason="passing historical screen registered as Shadow",
    )
    indicators = pd.DataFrame(
        {"Close": [100.0]},
        index=pd.to_datetime(["2026-08-05"]),
    )
    parity_result = evaluate_data_access_parity(
        legacy_indicators=indicators,
        migrated_indicators=indicators.copy(),
        legacy_signals=(),
        migrated_signals=(),
        legacy_trades=(),
        migrated_trades=(),
    )
    outputs = DataAccessParityOutputs(indicators, (), ())
    evidence = run_verified_data_access_parity(
        snapshot_id="c" * 64,
        detector_identity=strategy.experiment_name,
        result_fingerprint="a" * 64,
        snapshot_loader=lambda _snapshot_id: object(),
        legacy_runner=lambda _bundle: outputs,
        migrated_runner=lambda _bundle: outputs,
    )
    assert evidence.result == parity_result
    parity = reader.record_migration_parity(
        strategy,
        evidence=evidence,
        occurred_at=datetime(2026, 8, 7, 13, 0, tzinfo=UTC),
    )

    class Qualification:
        def read(self):
            return {
                "events": [
                    {
                        "event_id": "shadow-registration:shadow-1",
                        "event_type": "shadow_registration",
                        "payload": {
                            "shadow_id": "shadow-1",
                            "definition_fingerprint": "a" * 64,
                        },
                    },
                    {
                        "event_id": "activation-evaluation:shadow-1:2027-08-08",
                        "event_type": "activation_evaluation",
                        "payload": {
                            "shadow_id": "shadow-1",
                            "eligible": True,
                            "disposition": "activation-eligible",
                        },
                    },
                ]
            }

    verifier = FollowupActivationVerifier(
        qualification_registry=Qualification(),
        lifecycle_registry=reader,
        current_result_fingerprint_resolver=lambda _strategy: "a" * 64,
    )
    writer = FollowupLifecycleRegistry(path, activation_verifier=verifier)
    active = writer.activate_strategy(
        strategy,
        proof=FollowupActivationProof(
            shadow_id="shadow-1",
            qualification_event_id="activation-evaluation:shadow-1:2027-08-08",
            result_fingerprint="a" * 64,
            parity_digest=parity.parity_digest,
        ),
        occurred_at=datetime(2027, 8, 8, 12, 0, tzinfo=UTC),
        reason="prospective qualification passed",
    )

    assert active.status_for(strategy.ticker, strategy.experiment_name) is (
        StrategyLifecycle.ACTIVE
    )


def test_documented_data_consistency_correction_is_explicit_and_non_blocking() -> None:
    index = pd.to_datetime(["2026-08-03"])
    legacy = pd.DataFrame({"Close": [100.0]}, index=index)
    migrated = pd.DataFrame({"Close": [99.5]}, index=index)
    correction = DataAccessParityCorrection(
        difference_id="indicator:2026-08-03T00:00:00:Close",
        reason="validated adjusted-price correction in the immutable snapshot",
    )

    result = evaluate_data_access_parity(
        legacy_indicators=legacy,
        migrated_indicators=migrated,
        legacy_signals=(),
        migrated_signals=(),
        legacy_trades=(),
        migrated_trades=(),
        corrections=(correction,),
    )

    assert result.passed is True
    assert result.differences[0].classification == "documented_correction"
    assert result.differences[0].reason == correction.reason


def test_unused_or_duplicate_parity_corrections_fail_closed() -> None:
    frame = pd.DataFrame({"Close": [100.0]}, index=pd.to_datetime(["2026-08-03"]))
    correction = DataAccessParityCorrection("indicator:unused:Close", "fixture")

    with pytest.raises(ValueError, match="does not match a difference"):
        evaluate_data_access_parity(
            legacy_indicators=frame,
            migrated_indicators=frame.copy(),
            legacy_signals=(),
            migrated_signals=(),
            legacy_trades=(),
            migrated_trades=(),
            corrections=(correction,),
        )
    with pytest.raises(ValueError, match="unique"):
        evaluate_data_access_parity(
            legacy_indicators=frame,
            migrated_indicators=frame.copy(),
            legacy_signals=(),
            migrated_signals=(),
            legacy_trades=(),
            migrated_trades=(),
            corrections=(correction, correction),
        )


@pytest.mark.parametrize(
    ("lifecycle", "has_position", "expected"),
    [
        (StrategyLifecycle.LEGACY_ACTIVE, True, "legacy position management"),
        (StrategyLifecycle.RETIRING, True, "legacy position management"),
        (StrategyLifecycle.LEGACY_ACTIVE, False, "migration pending"),
        (StrategyLifecycle.MIGRATION_PENDING, False, "migration pending"),
        (StrategyLifecycle.HISTORICAL_SCREEN_FAILED, False, "historical screen failed"),
        (StrategyLifecycle.SHADOW, False, "Shadow"),
        (StrategyLifecycle.INSUFFICIENT_EVIDENCE, False, "insufficient evidence"),
        (StrategyLifecycle.ACTIVE, False, "Active"),
    ],
)
def test_followup_status_report_uses_phase_7_ticker_vocabulary(
    lifecycle: StrategyLifecycle,
    has_position: bool,
    expected: str,
) -> None:
    report = build_followup_status_report(
        _strategy(),
        _buy_context(lifecycle=lifecycle, has_actual_position=has_position),
    )

    assert report.ticker == "SPY"
    assert report.state == expected
    assert report.lifecycle is lifecycle


def test_status_report_exposes_exact_buy_block_or_authorization() -> None:
    blocked = build_followup_status_report(
        _strategy(),
        _buy_context(lifecycle=StrategyLifecycle.SHADOW),
    )
    active = build_followup_status_report(_strategy(), _buy_context())

    assert blocked.buy_authorized is False
    assert blocked.buy_reason == "strategy is shadow"
    assert active.buy_authorized is True
    assert active.buy_reason == "authorized"
