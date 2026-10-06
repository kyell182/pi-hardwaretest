"""Groene ACT-led als eindsignaal, zodat je geen scherm nodig hebt."""
from pathlib import Path


class StatusLed:
    def __init__(self, name: str = "ACT"):
        self._base = Path("/sys/class/leds") / name

    def _write(self, attribute: str, value: str) -> None:
        try:
            (self._base / attribute).write_text(value)
        except OSError:
            pass  # led niet beschikbaar: geen probleem, rapport blijft de bron

    def busy(self) -> None:
        """Traag knipperen = test bezig."""
        self._blink(on_ms=1000, off_ms=1000)

    def success(self) -> None:
        """Hartslag-patroon = alles goed."""
        self._write("trigger", "heartbeat")

    def failure(self) -> None:
        """Snel knipperen = minstens één fout."""
        self._blink(on_ms=100, off_ms=100)

    def _blink(self, on_ms: int, off_ms: int) -> None:
        self._write("trigger", "timer")
        self._write("delay_on", str(on_ms))
        self._write("delay_off", str(off_ms))
