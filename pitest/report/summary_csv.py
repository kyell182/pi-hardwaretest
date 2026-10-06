"""Overzicht van alle geteste Pi's in één CSV (opent in Excel)."""
import csv
from datetime import datetime
from pathlib import Path

from pitest.core.result import CheckResult
from pitest.hardware.board import BoardInfo


class SummaryCsv:
    def __init__(self, path: Path):
        self._path = path

    def append(self, board: BoardInfo, results: list[CheckResult], verdict: str) -> None:
        is_new = not self._path.exists()
        with open(self._path, "a", newline="", encoding="utf-8") as fh:
            writer = csv.writer(fh, delimiter=";")
            if is_new:
                writer.writerow(["datum", "serienummer", "model", "ram_mb", "oordeel"]
                                + [r.name for r in results])
            writer.writerow([datetime.now().strftime("%Y-%m-%d %H:%M"), board.serial, board.model,
                             board.detected_ram_mb, verdict] + [r.status.value for r in results])
