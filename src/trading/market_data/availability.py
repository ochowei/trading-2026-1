"""Opt-in auxiliary availability policies beyond the released v001 default."""

from dataclasses import dataclass
from enum import StrEnum

from trading.market_data.models import AvailabilityPolicy


class ExcessObservationLagMode(StrEnum):
    """How a declared auxiliary dependency handles an over-age observation."""

    FAIL = "fail"
    MARK_UNAVAILABLE = "mark_unavailable"


@dataclass(frozen=True, slots=True)
class GapAwareAvailabilityPolicy(AvailabilityPolicy):
    """Explicitly preserve over-age rows as unavailable audit evidence."""

    excess_lag_mode: ExcessObservationLagMode = ExcessObservationLagMode.MARK_UNAVAILABLE

    def __post_init__(self) -> None:
        AvailabilityPolicy.__post_init__(self)
        try:
            mode = ExcessObservationLagMode(self.excess_lag_mode)
        except ValueError as exc:
            raise ValueError(
                f"unsupported excess observation lag mode: {self.excess_lag_mode}"
            ) from exc
        object.__setattr__(self, "excess_lag_mode", mode)
