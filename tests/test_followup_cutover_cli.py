from datetime import UTC, datetime

import pytest

from trading.cli import build_parser, main
from trading.core.followup_cutover import (
    FollowupLifecycleRegistry,
    FollowupStrategy,
)


def test_followup_state_init_fails_closed_before_writing(tmp_path) -> None:
    lifecycle = tmp_path / "followup-lifecycle.json"

    with pytest.raises(SystemExit, match="legacy experiment research is retired"):
        main(["followup-state", "init", "--path", str(lifecycle)])

    assert not lifecycle.exists()


def test_followup_state_resume_fails_closed_without_changing_lifecycle(tmp_path) -> None:
    path = tmp_path / "followup-lifecycle.json"
    registry = FollowupLifecycleRegistry(path)

    registry.initialize_cutover(
        (FollowupStrategy("SPY", "spy_007_trend_pullback"),),
        occurred_at=datetime(2026, 8, 6, 12, 0, tzinfo=UTC),
    )
    before = path.read_bytes()

    with pytest.raises(SystemExit, match="legacy experiment research is retired"):
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

    assert path.read_bytes() == before
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
