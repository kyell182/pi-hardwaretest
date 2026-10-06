"""Leesbaar tekstrapport per Pi."""
from datetime import datetime
from pathlib import Path

from pitest.core.result import CheckResult
from pitest.hardware.board import BoardInfo


class TextReport:
    def __init__(self, directory: Path):
        self._directory = directory

    def write(self, board: BoardInfo, results: list[CheckResult], verdict: str) -> Path:
        stamp = datetime.now().strftime("%Y%m%d-%H%M")
        path = self._directory / f"testrapport-{board.serial}-{stamp}.txt"
        path.write_text(self._render(board, results, verdict, stamp), encoding="utf-8")
        return path

    @staticmethod
    def _render(board: BoardInfo, results: list[CheckResult], verdict: str, stamp: str) -> str:
        lines = [
            "RASPBERRY PI HARDWARETEST",
            "=" * 60,
            f"Model:       {board.model}",
            f"Serienummer: {board.serial}",
            f"Datum:       {stamp}",
            f"EINDOORDEEL: {verdict}",
            "=" * 60, "",
        ]
        for r in results:
            lines.append(f"[{r.status.value:^12}] {r.name}: {r.summary}  ({r.duration_s:.0f}s)")
            lines += [f"               - {d}" for d in r.details]
            lines.append("")
        return "\n".join(lines)
