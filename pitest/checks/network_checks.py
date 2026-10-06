"""Ethernet, wifi en bluetooth."""
from pathlib import Path

from pitest.core.check import Check
from pitest.core.result import Status
from pitest.core.shell import Shell

NET = Path("/sys/class/net")


def _read(path: Path) -> str:
    try:
        return path.read_text().strip()
    except OSError:
        return ""


class EthernetCheck(Check):
    name = "Ethernet"

    def __init__(self, ping_host: str, interface: str = "eth0"):
        self._host = ping_host
        self._iface = interface

    def _execute(self):
        if not (NET / self._iface).exists():
            return self._result(Status.FAIL, f"{self._iface} niet gevonden")
        if _read(NET / self._iface / "carrier") != "1":
            return self._result(Status.WARN, "Geen kabel ingeplugd (of poort defect)")
        speed = _read(NET / self._iface / "speed")
        details = [f"Linksnelheid: {speed} Mbit/s"]
        ping = Shell.run(["ping", "-c", "5", "-I", self._iface, self._host], timeout=30)
        details.append(ping.stdout.splitlines()[-1] if ping.stdout else ping.stderr)
        if not ping.ok:
            return self._result(Status.WARN, "Link ok, maar geen internet via ethernet", details)
        if speed and speed != "1000":
            return self._result(Status.WARN, f"Werkt, maar slechts {speed} Mbit/s (kabel?)", details)
        return self._result(Status.PASS, "Gigabit-link en internet ok", details)


class WifiCheck(Check):
    name = "Wifi"

    def __init__(self, interface: str = "wlan0"):
        self._iface = interface

    def _execute(self):
        if not (NET / self._iface).exists():
            return self._result(Status.FAIL, "Geen wifi-chip gevonden")
        Shell.run(["rfkill", "unblock", "wifi"])
        Shell.run(["ip", "link", "set", self._iface, "up"])
        scan = Shell.run(["iw", "dev", self._iface, "scan"], timeout=30)
        networks = {line.split(":", 1)[1].strip()
                    for line in scan.stdout.splitlines() if line.strip().startswith("SSID:")}
        networks.discard("")
        details = [f"Gevonden netwerken: {len(networks)}"]
        if not scan.ok:
            return self._result(Status.WARN, f"Scan mislukt: {scan.stderr[:100]}", details)
        if not networks:
            return self._result(Status.WARN, "Geen netwerken gezien (antenne?)", details)
        return self._result(Status.PASS, f"Wifi werkt, {len(networks)} netwerken gezien", details)


class BluetoothCheck(Check):
    name = "Bluetooth"

    def _execute(self):
        adapters = list(Path("/sys/class/bluetooth").glob("hci*"))
        if not adapters:
            return self._result(Status.FAIL, "Geen bluetooth-adapter gevonden")
        return self._result(Status.PASS, f"Adapter gevonden: {adapters[0].name}")
