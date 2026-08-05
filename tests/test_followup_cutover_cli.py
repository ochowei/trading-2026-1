from datetime import UTC, datetime

from trading.cli import build_parser, main
from trading.core.followup_cutover import (
    FollowupLifecycleRegistry,
    FollowupStrategy,
    StrategyLifecycle,
)
from trading.core.manual_ledger import BROKER_COLUMNS


def test_followup_state_init_requires_current_reconciliation_and_marks_legacy(
    tmp_path,
    monkeypatch,
    capsys,
) -> None:
    ledger = tmp_path / "ledger.csv"
    broker = tmp_path / "broker.csv"
    reconciliation = tmp_path / "reconciliation.json"
    lifecycle = tmp_path / "followup-lifecycle.json"
    strategy = {
        "ticker": "SPY",
        "experiment_name": "spy_007_trend_pullback",
        "label": "SPY-007",
        "has_trailing_stop": False,
    }
    monkeypatch.setattr("trading.followup.STRATEGIES", [strategy])
    main(
        [
            "ledger",
            "init",
            "--path",
            str(ledger),
            "--managed-capital",
            "1000",
            "--universe",
            "SPY",
            "--timestamp",
            "2026-08-05T12:00:00Z",
        ]
    )
    broker.write_text(
        ",".join(BROKER_COLUMNS) + "\n" + "cash,SPY,,,,1000\n",
        encoding="utf-8",
    )
    main(
        [
            "ledger",
            "reconcile",
            "--path",
            str(ledger),
            "--broker-export",
            str(broker),
            "--report",
            str(reconciliation),
        ]
    )

    main(
        [
            "followup-state",
            "init",
            "--path",
            str(lifecycle),
            "--ledger-path",
            str(ledger),
            "--reconciliation-path",
            str(reconciliation),
            "--timestamp",
            "2026-08-06T12:00:00Z",
        ]
    )
    main(["followup-state", "status", "--path", str(lifecycle)])

    state = FollowupLifecycleRegistry(lifecycle).read()
    assert state.no_new_entry is True
    assert state.status_for("SPY", "spy_007_trend_pullback") is (StrategyLifecycle.LEGACY_ACTIVE)
    output = capsys.readouterr().out
    assert "controlled followup cutover initialized" in output
    assert "new entries: paused" in output
    assert "SPY/spy_007_trend_pullback: legacy_active" in output


def test_followup_state_mode_supports_reversible_no_new_entry(tmp_path) -> None:
    path = tmp_path / "followup-lifecycle.json"
    registry = FollowupLifecycleRegistry(path)

    registry.initialize_cutover(
        (FollowupStrategy("SPY", "spy_007_trend_pullback"),),
        occurred_at=datetime(2026, 8, 6, 12, 0, tzinfo=UTC),
    )

    main(
        [
            "followup-state",
            "resume",
            "--path",
            str(path),
            "--reason",
            "controlled activation",
            "--timestamp",
            "2026-08-07T12:00:00Z",
        ]
    )
    assert registry.read().no_new_entry is False
    main(
        [
            "followup-state",
            "pause",
            "--path",
            str(path),
            "--reason",
            "operator rollback",
            "--timestamp",
            "2026-08-08T12:00:00Z",
        ]
    )
    assert registry.read().no_new_entry is True


def test_followup_state_exposes_verified_activation_inputs() -> None:
    args = build_parser().parse_args(
        [
            "followup-state",
            "activate",
            "--ticker",
            "SPY",
            "--experiment",
            "spy_007_trend_pullback",
            "--shadow-id",
            "shadow-1",
            "--qualification-event-id",
            "activation-evaluation:shadow-1:2027-08-08",
            "--result-fingerprint",
            "a" * 64,
            "--parity-digest",
            "b" * 64,
            "--reason",
            "prospective qualification passed",
        ]
    )

    assert args.followup_state_command == "activate"
    assert args.qualification_path.name == "qualification-registry.json"
