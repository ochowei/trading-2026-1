import json
from datetime import UTC, datetime

from trading.cli import build_parser, main
from trading.core.live_drift import (
    DriftDirection,
    DriftMetricExpectation,
    DriftMetricKind,
    PredictiveDriftEnvelope,
)
from trading.core.manual_ledger import LedgerInitialization, ManualLedgerStore


def _envelope() -> PredictiveDriftEnvelope:
    return PredictiveDriftEnvelope.create(
        strategy_id="SPY/spy_007_trend_pullback",
        definition_fingerprint="a" * 64,
        source_identities=("historical-plan-1", "shadow-1"),
        metrics=(
            DriftMetricExpectation.create(
                metric_id="performance_return",
                kind=DriftMetricKind.EXECUTION,
                direction=DriftDirection.LOWER_IS_WORSE,
                watch_boundary="-0.20",
                pause_boundary="-0.40",
                minimum_observations=1,
                window_sessions=126,
            ),
        ),
        activation_anchor=datetime(2026, 8, 7, tzinfo=UTC).date(),
        checkpoint_interval_sessions=21,
        bootstrap_seed=7,
        bootstrap_repetitions=1000,
        bootstrap_block_sessions=5,
        frozen_at=datetime(2026, 8, 6, 12, 0, tzinfo=UTC),
    )


def test_drift_cli_parser_exposes_read_only_status_and_state_changes() -> None:
    status = build_parser().parse_args(["drift", "status"])
    observe = build_parser().parse_args(
        [
            "drift",
            "observe",
            "--path",
            "state/live-drift/spy.json",
            "--session",
            "2026-09-08",
            "--metric",
            "performance_return=0:1",
        ]
    )

    assert status.drift_command == "status"
    assert observe.drift_command == "observe"
    assert observe.shadow_evidence_event_id is None


def test_drift_cli_freeze_activate_observe_checkpoint_and_status(tmp_path, capsys) -> None:
    registry_path = tmp_path / "live-drift.json"
    manifest = tmp_path / "envelope.json"
    envelope = _envelope()
    ledger_path = tmp_path / "manual-ledger.csv"
    ManualLedgerStore(ledger_path).initialize(
        LedgerInitialization.create(
            managed_capital="1000",
            universe=("SPY",),
            initialized_at=datetime(2026, 8, 6, 11, 0, tzinfo=UTC),
        )
    )
    manifest.write_text(
        json.dumps(envelope.payload()),
        encoding="utf-8",
    )

    main(["drift", "freeze", "--path", str(registry_path), "--envelope", str(manifest)])
    main(
        [
            "drift",
            "activate",
            "--path",
            str(registry_path),
            "--strategy-id",
            envelope.strategy_id,
            "--envelope-id",
            envelope.envelope_id,
            "--activation-event-id",
            "strategy_activated:test",
            "--timestamp",
            "2026-08-07T21:00:00Z",
        ]
    )
    main(
        [
            "drift",
            "observe",
            "--path",
            str(registry_path),
            "--session",
            "2026-09-08",
            "--observed-at",
            "2026-09-08T21:00:00Z",
            "--metric",
            "performance_return=0:1",
            "--ledger-path",
            str(ledger_path),
        ]
    )
    main(
        [
            "drift",
            "checkpoint",
            "--path",
            str(registry_path),
            "--ordinal",
            "1",
            "--session",
            "2026-09-08",
            "--timestamp",
            "2026-09-08T21:00:00Z",
        ]
    )
    main(["drift", "status", "--path", str(registry_path)])

    output = capsys.readouterr().out
    assert "drift state: healthy" in output
    assert "buy allowed: True" in output
    assert f"envelope: {envelope.envelope_id}" in output
