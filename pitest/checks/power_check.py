"""Controleert voeding (onderspanning) en throttling via de firmware."""
from pitest.core.check import Check
from pitest.core.result import Status
from pitest.hardware.vcgencmd import Vcgencmd

UNDERVOLTAGE_BITS = (1 << 0) | (1 << 16)


class PowerCheck(Check):
    name = "Voeding & throttling"

    def __init__(self, vc: Vcgencmd):
        self._vc = vc

    def _execute(self):
        if not self._vc.available():
            return self._result(Status.SKIP, "vcgencmd niet gevonden")
        value = self._vc.throttled()
        if value is None:
            return self._result(Status.WARN, "Kon throttle-status niet lezen")
        details = [f"get_throttled = 0x{value:x}", f"Kernspanning: {self._vc.core_voltage()}"]
        flags = self._vc.describe_throttle(value)
        details += flags
        if value & UNDERVOLTAGE_BITS:
            return self._result(Status.FAIL, "Onderspanning: test eerst met een andere voeding/kabel", details)
        if flags:
            return self._result(Status.WARN, "Afgeremd geweest (meestal temperatuur)", details)
        return self._result(Status.PASS, "Geen onderspanning of throttling", details)
