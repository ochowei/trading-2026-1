import pytest

from trading.cli import build_parser, main
from trading.core.manual_ledger import BROKER_COLUMNS, ManualLedgerStore


def test_ledger_parser_exposes_all_phase_five_operations(tmp_path) -> None:
    path = tmp_path / "ledger.csv"
    args = build_parser().parse_args(
        [
            "ledger",
            "init",
            "--path",
            str(path),
            "--managed-capital",
            "1000.00",
            "--universe",
            "SPY",
            "QQQ",
        ]
    )
    assert args.command == "ledger"
    assert args.ledger_command == "init"
    assert args.universe == ["SPY", "QQQ"]

    for command in ("verify", "record", "reconcile", "export", "import"):
        assert build_parser().parse_args(["ledger", command]).ledger_command == command


def test_ledger_cli_init_verify_and_export_import_are_local_and_deterministic(
    tmp_path, capsys
) -> None:
    path = tmp_path / "ledger.csv"
    backup = tmp_path / "backup.csv"
    imported = tmp_path / "imported.csv"
    main(
        [
            "ledger",
            "init",
            "--path",
            str(path),
            "--managed-capital",
            "1000",
            "--universe",
            "SPY",
            "--timestamp",
            "2026-08-05T12:00:00Z",
        ]
    )
    main(["ledger", "verify", "--path", str(path)])
    main(["ledger", "export", "--path", str(path), str(backup)])
    main(["ledger", "import", "--path", str(imported), str(backup)])
    output = capsys.readouterr().out
    assert "ledger initialized" in output
    assert "ledger valid" in output
    assert "exported" in output
    assert "imported" in output
    assert ManualLedgerStore(imported).verify().cash == 1000


def test_ledger_cli_record_and_reconcile_fail_closed_on_mismatch(tmp_path, capsys) -> None:
    path = tmp_path / "ledger.csv"
    broker = tmp_path / "broker.csv"
    report = tmp_path / "reconcile.json"
    main(
        [
            "ledger",
            "init",
            "--path",
            str(path),
            "--managed-capital",
            "1000",
            "--universe",
            "SPY",
            "--timestamp",
            "2026-08-05T12:00:00Z",
        ]
    )
    main(
        [
            "ledger",
            "record",
            "--path",
            str(path),
            "--event-type",
            "deposit",
            "--amount",
            "10",
            "--timestamp",
            "2026-08-05T12:01:00Z",
        ]
    )
    broker.write_text(",".join(BROKER_COLUMNS) + "\n" + "cash,SPY,,,,1000\n", encoding="utf-8")
    with pytest.raises(SystemExit) as exc_info:
        main(
            [
                "ledger",
                "reconcile",
                "--path",
                str(path),
                "--broker-export",
                str(broker),
                "--report",
                str(report),
            ]
        )
    assert exc_info.value.code == 1
    assert report.exists()
    assert "failed" in capsys.readouterr().out
