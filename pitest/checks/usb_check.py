"""Toont welke USB-apparaten herkend worden."""
from pitest.core.check import Check
from pitest.core.result import Status
from pitest.core.shell import Shell


class UsbCheck(Check):
    name = "USB-poorten"

    def _execute(self):
        if not Shell.available("lsusb"):
            return self._result(Status.SKIP, "lsusb niet geïnstalleerd")
        lines = Shell.run(["lsusb"]).stdout.splitlines()
        # Interne hubs (bv. VIA Labs op de Pi 4) zijn geen ingeplugde apparaten
        devices = [line for line in lines if "hub" not in line.lower()]
        details = devices or ["Enkel interne hubs gevonden"]
        if not devices:
            return self._result(Status.WARN, "Geen USB-apparaten: steek sticks in alle poorten om ze te testen",
                                details)
        return self._result(Status.PASS, f"{len(devices)} USB-apparaat/apparaten herkend", details)
