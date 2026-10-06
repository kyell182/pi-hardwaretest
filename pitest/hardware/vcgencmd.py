"""Uitlezen van de VideoCore-firmware (temperatuur, spanning, throttling)."""
import re

from pitest.core.shell import Shell

THROTTLE_FLAGS = {
    0: "onderspanning NU",
    1: "kloksnelheid begrensd NU",
    2: "afgeremd (throttled) NU",
    3: "zachte temperatuurlimiet NU",
    16: "onderspanning opgetreden sinds boot",
    17: "kloksnelheid begrensd sinds boot",
    18: "afgeremd sinds boot",
    19: "zachte temperatuurlimiet sinds boot",
}


class Vcgencmd:
    def available(self) -> bool:
        return Shell.available("vcgencmd")

    def temperature_c(self) -> float | None:
        out = Shell.run(["vcgencmd", "measure_temp"]).stdout
        match = re.search(r"([\d.]+)", out)
        return float(match.group(1)) if match else None

    def throttled(self) -> int | None:
        out = Shell.run(["vcgencmd", "get_throttled"]).stdout
        match = re.search(r"0x([0-9a-fA-F]+)", out)
        return int(match.group(1), 16) if match else None

    def core_voltage(self) -> str:
        return Shell.run(["vcgencmd", "measure_volts", "core"]).stdout or "onbekend"

    @staticmethod
    def describe_throttle(value: int) -> list[str]:
        return [text for bit, text in THROTTLE_FLAGS.items() if value & (1 << bit)]
