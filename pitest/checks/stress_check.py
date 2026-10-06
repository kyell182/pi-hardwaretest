"""Belast alle CPU-kernen en volgt de temperatuur."""
import time

from pitest.core.check import Check
from pitest.core.result import Status
from pitest.core.shell import Shell
from pitest.hardware.vcgencmd import Vcgencmd

SAMPLE_INTERVAL_S = 10


class StressCheck(Check):
    name = "CPU-belasting & temperatuur"

    def __init__(self, vc: Vcgencmd, minutes: int, max_temp_c: float):
        self._vc = vc
        self._seconds = minutes * 60
        self._max_temp = max_temp_c

    def _execute(self):
        if not Shell.available("stress-ng"):
            return self._result(Status.SKIP, "stress-ng niet geïnstalleerd")
        idle = self._vc.temperature_c()
        process = Shell.start(["stress-ng", "--cpu", "0", "--cpu-method", "all",
                               "--timeout", f"{self._seconds}s"])
        peak = self._monitor(process)
        exit_code = process.wait()
        details = [f"Duur: {self._seconds // 60} min", f"Temp. in rust: {idle} °C",
                   f"Piektemperatuur: {peak} °C", f"stress-ng exitcode: {exit_code}"]
        if exit_code != 0:
            return self._result(Status.FAIL, "CPU-fouten tijdens belasting", details)
        if peak is not None and peak >= self._max_temp:
            return self._result(Status.WARN, "Wordt erg warm: koeling nakijken", details)
        return self._result(Status.PASS, f"Stabiel onder volle belasting, max {peak} °C", details)

    def _monitor(self, process) -> float | None:
        peak = None
        while process.poll() is None:
            temp = self._vc.temperature_c()
            if temp is not None:
                peak = temp if peak is None else max(peak, temp)
            time.sleep(SAMPLE_INTERVAL_S)
        return peak
