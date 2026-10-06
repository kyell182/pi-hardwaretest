#!/usr/bin/env bash
# Installeert de hardwaretest op een verse Raspberry Pi OS Lite (64-bit).
# Eenmalig uitvoeren op de test-SD-kaart:  sudo ./install.sh
set -euo pipefail

if [[ $EUID -ne 0 ]]; then
  echo "Voer uit met sudo: sudo ./install.sh" >&2
  exit 1
fi

SRC="$(cd "$(dirname "$0")" && pwd)"
BOOT=/boot/firmware
[[ -f $BOOT/config.txt ]] || BOOT=/boot

echo "==> Pakketten installeren"
apt-get update
apt-get install -y stress-ng memtester usbutils iw rfkill

echo "==> Testcode kopiëren naar /opt/pitest"
rm -rf /opt/pitest
mkdir -p /opt/pitest
cp -r "$SRC/pitest" /opt/pitest/

echo "==> Instellingen op bootpartitie zetten"
[[ -f $BOOT/pitest.conf ]] || cp "$SRC/pitest.conf" "$BOOT/pitest.conf"

echo "==> Automatisch starten bij elke boot"
cp "$SRC/systemd/pitest.service" /etc/systemd/system/
systemctl daemon-reload
systemctl enable pitest.service

echo "Klaar. Vanaf de volgende boot draait de test automatisch."
echo "Nu meteen testen:  sudo systemctl start pitest"
