"""Schrijf/lees-test van de opslag (SD-kaart of NVMe) met controle op corruptie."""
import hashlib
import os
import time
from pathlib import Path

from pitest.core.check import Check
from pitest.core.result import Status
from pitest.core.shell import Shell

CHUNK = 4 * 1024 * 1024
MIN_WRITE_MBS = 5.0


class StorageCheck(Check):
    name = "Opslag schrijven/lezen"

    def __init__(self, size_mb: int, target_dir: Path = Path("/var/tmp")):
        self._size_mb = size_mb
        self._file = target_dir / "pitest-storage.bin"

    def _execute(self):
        try:
            written_hash, write_speed = self._write()
            self._drop_caches()
            read_hash, read_speed = self._read()
        finally:
            self._file.unlink(missing_ok=True)
        details = [f"Schrijven: {write_speed:.1f} MB/s", f"Lezen: {read_speed:.1f} MB/s"]
        details += self._kernel_errors()
        if written_hash != read_hash:
            return self._result(Status.FAIL, "Gelezen data wijkt af: opslag of controller defect", details)
        if len(details) > 2:
            return self._result(Status.WARN, "Kernel meldt opslagfouten", details)
        if write_speed < MIN_WRITE_MBS:
            return self._result(Status.WARN, "Zeer trage schrijfsnelheid", details)
        return self._result(Status.PASS, f"{self._size_mb} MB foutloos geschreven en gelezen", details)

    def _write(self) -> tuple[str, float]:
        digest = hashlib.sha256()
        start = time.monotonic()
        with open(self._file, "wb") as fh:
            for _ in range(self._size_mb * 1024 * 1024 // CHUNK):
                block = os.urandom(CHUNK)
                digest.update(block)
                fh.write(block)
            fh.flush()
            os.fsync(fh.fileno())
        return digest.hexdigest(), self._size_mb / (time.monotonic() - start)

    def _read(self) -> tuple[str, float]:
        digest = hashlib.sha256()
        start = time.monotonic()
        with open(self._file, "rb") as fh:
            while block := fh.read(CHUNK):
                digest.update(block)
        return digest.hexdigest(), self._size_mb / (time.monotonic() - start)

    @staticmethod
    def _drop_caches() -> None:
        try:
            Path("/proc/sys/vm/drop_caches").write_text("3")
        except OSError:
            pass

    @staticmethod
    def _kernel_errors() -> list[str]:
        log = Shell.run(["dmesg"]).stdout.splitlines()
        keywords = ("mmc", "nvme", "I/O error")
        return [line for line in log if "error" in line.lower() and any(k in line for k in keywords)][:5]
