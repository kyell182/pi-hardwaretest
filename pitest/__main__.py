"""Startpunt: python3 -m pitest"""
from pitest.checks.board_check import BoardCheck
from pitest.checks.gpio_check import GpioLoopbackCheck
from pitest.checks.memory_check import MemoryCheck
from pitest.checks.network_checks import BluetoothCheck, EthernetCheck, WifiCheck
from pitest.checks.power_check import PowerCheck
from pitest.checks.storage_check import StorageCheck
from pitest.checks.stress_check import StressCheck
from pitest.checks.usb_check import UsbCheck
from pitest.core.config import Config
from pitest.core.paths import boot_partition
from pitest.core.result import Status
from pitest.hardware.board import BoardInfo
from pitest.hardware.led import StatusLed
from pitest.hardware.vcgencmd import Vcgencmd
from pitest.report.summary_csv import SummaryCsv
from pitest.report.text_report import TextReport
from pitest.suite import TestSuite


def build_checks(board: BoardInfo, config: Config) -> list:
    vc = Vcgencmd()
    return [
        BoardCheck(board),
        EthernetCheck(config.ping_host),
        WifiCheck(),
        BluetoothCheck(),
        UsbCheck(),
        StorageCheck(config.storage_test_mb),
        MemoryCheck(config.memtest_mb),
        StressCheck(vc, config.stress_minutes, config.max_temp_c),
        PowerCheck(vc),  # als laatste: ziet ook onderspanning tijdens de stresstest
        GpioLoopbackCheck(config.gpio_pairs),
    ]


def main() -> int:
    boot = boot_partition()
    config = Config.load(boot / "pitest.conf")
    board = BoardInfo.detect()
    led = StatusLed()
    led.busy()

    suite = TestSuite(build_checks(board, config))
    results = suite.run(on_result=lambda r: print(f"[{r.status.value}] {r.name}: {r.summary}", flush=True))
    verdict = suite.verdict(results)

    report = TextReport(boot).write(board, results, verdict.value)
    SummaryCsv(boot / "pitest-overzicht.csv").append(board, results, verdict.value)
    print(f"Rapport: {report}")

    if verdict is Status.FAIL:
        led.failure()
        return 1
    led.success()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
