"""Canonical CSV encoding shared by the manual execution ledger boundary."""

from __future__ import annotations

import csv
import io
from collections.abc import Mapping, Sequence


class CanonicalCsvError(ValueError):
    """CSV bytes do not match the declared canonical schema and serialization."""


def canonical_csv_bytes(
    columns: Sequence[str],
    rows: Sequence[Mapping[str, str]],
) -> bytes:
    """Serialize fixed-schema rows with deterministic quoting and line endings."""
    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=columns, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return output.getvalue().encode("utf-8")


def parse_canonical_csv_bytes(
    content: bytes,
    columns: Sequence[str],
) -> tuple[dict[str, str], ...]:
    """Decode fixed-schema CSV and reject every non-canonical byte representation."""
    try:
        text = content.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise CanonicalCsvError("CSV is not valid UTF-8") from exc
    reader = csv.DictReader(io.StringIO(text, newline=""))
    if tuple(reader.fieldnames or ()) != tuple(columns):
        raise CanonicalCsvError("CSV header is not canonical")
    rows: list[dict[str, str]] = []
    try:
        for row in reader:
            if None in row or any(value is None for value in row.values()):
                raise CanonicalCsvError("CSV row does not match the canonical columns")
            rows.append({key: value for key, value in row.items() if key is not None})
    except csv.Error as exc:
        raise CanonicalCsvError("CSV is malformed") from exc
    canonical = canonical_csv_bytes(columns, rows)
    if canonical != content:
        raise CanonicalCsvError("CSV is not canonically serialized")
    return tuple(rows)
