"""Dunne wrapper rond subprocess, zodat tests geen subprocess-details kennen."""
import shutil
import subprocess
from dataclasses import dataclass


@dataclass
class CommandOutput:
    returncode: int
    stdout: str
    stderr: str

    @property
    def ok(self) -> bool:
        return self.returncode == 0


class Shell:
    @staticmethod
    def available(program: str) -> bool:
        return shutil.which(program) is not None

    @staticmethod
    def run(args: list[str], timeout: float = 60) -> CommandOutput:
        try:
            proc = subprocess.run(args, capture_output=True, text=True, timeout=timeout)
            return CommandOutput(proc.returncode, proc.stdout.strip(), proc.stderr.strip())
        except subprocess.TimeoutExpired:
            return CommandOutput(124, "", f"timeout na {timeout}s")
        except FileNotFoundError:
            return CommandOutput(127, "", f"{args[0]} niet gevonden")

    @staticmethod
    def start(args: list[str]) -> subprocess.Popen:
        return subprocess.Popen(args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
