"""Controleert of al het RAM-geheugen herkend wordt."""
from pitest.core.check import Check
from pitest.core.result import Status
from pitest.hardware.board import BoardInfo


class BoardCheck(Check):
    name = "Bord & geheugengrootte"

    def __init__(self, board: BoardInfo):
        self._board = board

    def _execute(self):
        b = self._board
        details = [f"Model: {b.model}", f"Revisie: {b.revision}",
                   f"RAM gedetecteerd: {b.detected_ram_mb} MB"]
        if b.expected_ram_mb is None:
            return self._result(Status.WARN, "Verwachte RAM-grootte onbekend", details)
        details.append(f"RAM volgens bord: {b.expected_ram_mb} MB")
        # Kernel en GPU reserveren een deel; minder dan 85% is verdacht
        if b.detected_ram_mb < b.expected_ram_mb * 0.85:
            return self._result(Status.FAIL, "Minder RAM gevonden dan het bord zou moeten hebben", details)
        return self._result(Status.PASS, f"{b.expected_ram_mb} MB RAM correct herkend", details)
