"""Gegevens over het bord: model, serienummer, verwachte RAM."""
from dataclasses import dataclass
from pathlib import Path

# Bits 20-22 van de nieuwe revisiecode = geheugengrootte
_RAM_BY_CODE_MB = {0: 256, 1: 512, 2: 1024, 3: 2048, 4: 4096, 5: 8192, 6: 16384}


@dataclass
class BoardInfo:
    model: str
    serial: str
    revision: str
    expected_ram_mb: int | None
    detected_ram_mb: int

    @property
    def family(self) -> int | None:
        for number in (5, 4):
            if f"Raspberry Pi {number}" in self.model or f"Compute Module {number}" in self.model:
                return number
        return None

    @classmethod
    def detect(cls) -> "BoardInfo":
        cpuinfo = cls._cpuinfo()
        revision = cpuinfo.get("Revision", "onbekend")
        return cls(
            model=cls._read("/proc/device-tree/model").rstrip("\x00") or cpuinfo.get("Model", "onbekend"),
            serial=cpuinfo.get("Serial", "onbekend").lstrip("0") or "onbekend",
            revision=revision,
            expected_ram_mb=cls._ram_from_revision(revision),
            detected_ram_mb=cls._mem_total_mb(),
        )

    @staticmethod
    def _read(path: str) -> str:
        try:
            return Path(path).read_text()
        except OSError:
            return ""

    @classmethod
    def _cpuinfo(cls) -> dict[str, str]:
        info = {}
        for line in cls._read("/proc/cpuinfo").splitlines():
            if ":" in line:
                key, value = line.split(":", 1)
                info[key.strip()] = value.strip()
        return info

    @staticmethod
    def _ram_from_revision(revision: str) -> int | None:
        try:
            code = int(revision, 16)
        except ValueError:
            return None
        if not code & (1 << 23):  # oude revisiecode-stijl
            return None
        return _RAM_BY_CODE_MB.get((code >> 20) & 0x7)

    @classmethod
    def _mem_total_mb(cls) -> int:
        for line in cls._read("/proc/meminfo").splitlines():
            if line.startswith("MemTotal:"):
                return int(line.split()[1]) // 1024
        return 0
