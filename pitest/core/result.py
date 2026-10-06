"""Resultaat van een individuele hardwaretest."""
from dataclasses import dataclass, field
from enum import Enum


class Status(Enum):
    PASS = "OK"
    WARN = "LET OP"
    FAIL = "FOUT"
    SKIP = "OVERGESLAGEN"

    @property
    def severity(self) -> int:
        return {Status.SKIP: 0, Status.PASS: 1, Status.WARN: 2, Status.FAIL: 3}[self]


@dataclass
class CheckResult:
    name: str
    status: Status
    summary: str
    details: list[str] = field(default_factory=list)
    duration_s: float = 0.0

    @property
    def is_failure(self) -> bool:
        return self.status is Status.FAIL
