"""Locatie van de bootpartitie (FAT, leesbaar op elke pc)."""
from pathlib import Path


def boot_partition() -> Path:
    for candidate in (Path("/boot/firmware"), Path("/boot")):
        if (candidate / "config.txt").exists():
            return candidate
    return Path("/boot")
