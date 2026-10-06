"""Schrijft en leest testpatronen in het RAM-geheugen."""
from pitest.core.check import Check
from pitest.core.result import Status
from pitest.core.shell import Shell


class MemoryCheck(Check):
    name = "RAM-geheugentest"

    def __init__(self, size_mb: int):
        self._size_mb = size_mb

    def _execute(self):
        if not Shell.available("memtester"):
            return self._result(Status.SKIP, "memtester niet geïnstalleerd")
        out = Shell.run(["memtester", f"{self._size_mb}M", "1"], timeout=3600)
        failures = [line.strip() for line in out.stdout.splitlines() if "FAILURE" in line]
        details = [f"Geteste hoeveelheid: {self._size_mb} MB"] + failures[:10]
        if out.returncode == 0:
            return self._result(Status.PASS, "Geen geheugenfouten", details)
        if failures:
            return self._result(Status.FAIL, "Geheugenfouten gevonden: RAM defect", details)
        return self._result(Status.WARN, f"memtester kon niet draaien: {out.stderr[:120]}", details)
