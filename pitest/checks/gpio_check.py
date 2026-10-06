"""Loopback-test: twee GPIO-pinnen met een jumperdraad verbonden."""
import time

from pitest.core.check import Check
from pitest.core.result import Status
from pitest.core.shell import Shell


class GpioLoopbackCheck(Check):
    name = "GPIO-loopback"

    def __init__(self, pairs: tuple[tuple[int, int], ...]):
        self._pairs = pairs

    def _execute(self):
        if not self._pairs:
            return self._result(Status.SKIP, "Geen pinparen ingesteld in pitest.conf")
        if not Shell.available("pinctrl"):
            return self._result(Status.SKIP, "pinctrl niet gevonden")
        details, broken = [], []
        for out_pin, in_pin in self._pairs:
            for a, b in ((out_pin, in_pin), (in_pin, out_pin)):  # beide richtingen
                ok = self._test(a, b)
                details.append(f"GPIO{a} -> GPIO{b}: {'ok' if ok else 'FOUT'}")
                if not ok:
                    broken.append(f"{a}->{b}")
        self._reset()
        if broken:
            return self._result(Status.FAIL, f"Pinnen werken niet: {', '.join(broken)}", details)
        return self._result(Status.PASS, f"{len(self._pairs)} pinpaar/paren ok", details)

    def _test(self, out_pin: int, in_pin: int) -> bool:
        Shell.run(["pinctrl", "set", str(in_pin), "ip", "pn"])
        for level, expected in (("dh", "hi"), ("dl", "lo")):
            Shell.run(["pinctrl", "set", str(out_pin), "op", level])
            time.sleep(0.05)
            if f"| {expected}" not in Shell.run(["pinctrl", "get", str(in_pin)]).stdout:
                return False
        return True

    def _reset(self) -> None:
        for pin in {p for pair in self._pairs for p in pair}:
            Shell.run(["pinctrl", "set", str(pin), "ip", "pd"])
