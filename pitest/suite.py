"""Voert alle tests na elkaar uit en bepaalt het eindoordeel."""
from pitest.core.check import Check
from pitest.core.result import CheckResult, Status


class TestSuite:
    def __init__(self, checks: list[Check]):
        self._checks = checks

    def run(self, on_result=None) -> list[CheckResult]:
        results = []
        for check in self._checks:
            result = check.run()
            results.append(result)
            if on_result:
                on_result(result)
        return results

    @staticmethod
    def verdict(results: list[CheckResult]) -> Status:
        worst = max((r.status for r in results), key=lambda s: s.severity, default=Status.SKIP)
        return Status.PASS if worst in (Status.PASS, Status.SKIP) else worst
