"""Instellingen, optioneel overschreven via pitest.conf op de bootpartitie."""
import configparser
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Config:
    stress_minutes: int = 10
    max_temp_c: float = 82.0
    memtest_mb: int = 512
    storage_test_mb: int = 256
    ping_host: str = "1.1.1.1"
    gpio_pairs: tuple[tuple[int, int], ...] = ()

    @classmethod
    def load(cls, path: Path) -> "Config":
        cfg = cls()
        if not path.exists():
            return cfg
        parser = configparser.ConfigParser()
        parser.read(path)
        section = parser["pitest"] if parser.has_section("pitest") else {}
        cfg.stress_minutes = int(section.get("stress_minutes", cfg.stress_minutes))
        cfg.max_temp_c = float(section.get("max_temp_c", cfg.max_temp_c))
        cfg.memtest_mb = int(section.get("memtest_mb", cfg.memtest_mb))
        cfg.storage_test_mb = int(section.get("storage_test_mb", cfg.storage_test_mb))
        cfg.ping_host = section.get("ping_host", cfg.ping_host)
        cfg.gpio_pairs = cls._parse_pairs(section.get("gpio_pairs", ""))
        return cfg

    @staticmethod
    def _parse_pairs(raw: str) -> tuple[tuple[int, int], ...]:
        """'17-27, 22-23' -> ((17, 27), (22, 23))"""
        pairs = []
        for item in filter(None, (p.strip() for p in raw.split(","))):
            a, b = item.split("-")
            pairs.append((int(a), int(b)))
        return tuple(pairs)
