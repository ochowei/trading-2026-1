from datetime import date

import pandas as pd
import pytest

from trading.cli import build_parser, main


class FakeInspection:
    state = "valid"
    errors = ()

    class metadata:
        data_cutoff = date(2026, 8, 4)
        last_incremental_refresh = None
        last_complete_refresh = None
        checksum = "a" * 64


class FakeDataService:
    def __init__(self):
        self.status_calls = []
        self.refresh_calls = []

    def status(self, series):
        self.status_calls.append(series)
        return FakeInspection()

    def refresh(self, series, *, mode, start, end):
        self.refresh_calls.append((series, mode, start, end))
        return pd.DataFrame(index=pd.to_datetime(["2026-08-04"]))


def test_data_cli_parser_exposes_status_and_refresh() -> None:
    status = build_parser().parse_args(["data", "status", "SPY"])
    refresh = build_parser().parse_args(
        ["data", "refresh", "^VIX", "--full", "--end", "2026-08-04"]
    )

    assert (status.command, status.data_command, status.symbol) == ("data", "status", "SPY")
    assert refresh.full is True
    assert refresh.start is None
    assert refresh.end == date(2026, 8, 4)


def test_data_status_is_diagnostic_only(monkeypatch, capsys) -> None:
    service = FakeDataService()
    monkeypatch.setattr("trading.cli.create_default_market_data_service", lambda: service)

    main(["data", "status", "SPY"])

    assert [item.symbol for item in service.status_calls] == ["SPY"]
    assert service.refresh_calls == []
    output = capsys.readouterr().out
    assert "SPY" in output
    assert "valid" in output
    assert "2026-08-04" in output


def test_data_refresh_is_explicit_and_reports_published_cutoff(monkeypatch, capsys) -> None:
    service = FakeDataService()
    monkeypatch.setattr("trading.cli.create_default_market_data_service", lambda: service)

    main(["data", "refresh", "SPY", "--full"])

    series, mode, start, end = service.refresh_calls[0]
    assert series.symbol == "SPY"
    assert mode == "full"
    assert start is None
    assert end is None
    assert "full refresh published" in capsys.readouterr().out


def test_data_full_refresh_rejects_partial_history_start(monkeypatch) -> None:
    service = FakeDataService()
    monkeypatch.setattr("trading.cli.create_default_market_data_service", lambda: service)

    with pytest.raises(SystemExit, match="full refresh always downloads complete history"):
        main(["data", "refresh", "SPY", "--full", "--start", "2020-01-01"])

    assert service.refresh_calls == []
