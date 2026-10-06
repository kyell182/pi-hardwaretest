"""Basisklasse voor alle hardwaretests."""
import time
import traceback
from abc import ABC, abstractmethod

from pitest.core.result import CheckResult, Status


class Check(ABC):
    """Eén test. Subklassen implementeren enkel `_execute`."""

    name: str = "Onbekende test"

    def run(self) -> CheckResult:
        start = time.monotonic()
        try:
            result = self._execute()
        except Exception as exc:  # een crashende test mag de rest niet stoppen
            result = CheckResult(
                self.name, Status.FAIL, f"Test crashte: {exc}",
                traceback.format_exc().splitlines()[-5:],
            )
        result.duration_s = time.monotonic() - start
        return result

    def _result(self, status: Status, summary: str, details=None) -> CheckResult:
        return CheckResult(self.name, status, summary, list(details or []))

    @abstractmethod
    def _execute(self) -> CheckResult:
        ...
