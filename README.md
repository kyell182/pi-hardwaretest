# Raspberry Pi hardwaretest (Pi 4 & Pi 5)

Eén SD-kaart die je van Pi naar Pi verplaatst. Bij elke boot test hij automatisch
de hardware en schrijft een rapport op de SD-kaart. Geen scherm of toetsenbord nodig.

## Testkaart maken

Je hoeft niets te installeren: er is een kant-en-klare image met alles erin.

1. Download **`pitest.img.xz`** (±1,4 GB) bij [Releases](../../releases) van deze repo.
2. Open **Raspberry Pi Imager**:
   - Apparaat: Raspberry Pi 4 of 5 (maakt niet uit, de kaart werkt in beide)
   - Besturingssysteem: scrol naar beneden → **Use custom** → kies `pitest.img.xz`
   - Opslag: je SD-kaart (minstens 8 GB, alles erop wordt gewist)
3. Vraagt Imager of je instellingen wil toepassen? Kies **Nee**. Alles zit al in de image.

Met balenaEtcher kan het ook: **Flash from file** → `pitest.img.xz` → kaart kiezen → **Flash**.

De eerste keer dat je de kaart opstart, breidt hij zich uit tot de volledige kaart en herstart hij één
keer. Daarna begint de test vanzelf.

Gegevens van de image:

|                        |                                                   |
| ---------------------- | ------------------------------------------------- |
| Hostname               | `pi-tester` (bereikbaar als `pi-tester.local`)    |
| Gebruiker / wachtwoord | `pitest` / `pitest`                               |
| SSH                    | aan, inloggen met wachtwoord                      |
| Wifi                   | niet ingesteld (de test gebruikt de netwerkkabel) |

Het wachtwoord staat bewust in deze README: het is een testkaart zonder gevoelige gegevens. Gebruik de
kaart wel niet als gewone Pi in een gedeeld netwerk.

## Een Pi testen

1. Kaart erin, **netwerkkabel erin**, eventueel USB-sticks in alle poorten.
2. Stroom aan met een **officiële voeding** (anders krijg je valse onderspanningsfouten).
3. Wacht tot de groene led verandert (~20 à 25 min met standaardinstellingen):

   | Groene led           | Betekenis         |
   | -------------------- | ----------------- |
   | traag knipperen (1s) | test bezig        |
   | hartslag (dubbel)    | geen fouten       |
   | snel knipperen       | minstens één FOUT |

4. Stroom eraf, kaart in je pc. Op de bootpartitie vind je:
   - `testrapport-<serienummer>-<datum>.txt`: het volledige rapport
   - `pitest-overzicht.csv`: één regel per geteste Pi (open in Excel)

## Live meekijken (optioneel)

Wil je zien hoe ver de test staat? Log in via SSH (`ssh pitest@pi-tester.local`, wachtwoord `pitest`)
en gebruik:

```bash
systemctl status pitest     # loopt de test nog?
journalctl -fu pitest       # volg de test live
```

Bij `systemctl status` betekent `activating (start)` dat de test nog bezig is. `inactive (dead)` met
`status=0/SUCCESS` betekent klaar zonder fouten, `status=1` betekent minstens één FOUT.

Met `journalctl -fu pitest` verschijnt er per afgewerkte test een regel. Stoppen met meekijken doe je
met `Ctrl+C`; de test zelf loopt gewoon verder. Zo ziet een volledige, geslaagde run eruit op een Pi 4:

![Voorbeeld van journalctl -fu pitest](docs/images/journalctl-voorbeeld.png)

Zo lees je die uitvoer:

- **`[OK] ...` / `[LET OP] ...`**: het resultaat van één test, in dezelfde volgorde als het rapport.
- **Stilte tussen twee regels is normaal.** Een regel verschijnt pas als een test klaar is. De RAM-test
  (hier 22:35 → 22:43) en de CPU-belasting (22:43 → 22:53) duren elk een paar minuten.
- **`stress-ng: invoked with ...`**: de start van de CPU-belasting op alle kernen.
- **`Rapport: /boot/firmware/testrapport-...txt`**: het rapport is weggeschreven, de test is klaar.
- **`Deactivated successfully`**: de service is netjes gestopt.
- **`Consumed 47min 47s CPU time`**: geen fout, maar de opgetelde processortijd van alle kernen samen.
  10 minuten belasting op 4 kernen is 40 minuten, plus ongeveer 8 minuten RAM-test op één kern.
- **`[LET OP] USB-poorten`** zoals hier: er zat geen USB-stick in. Steek sticks in om de poorten te testen.

Een eerste regel met een vreemde tijd (bv. `Starting pitest.service` om 21:58) is ook normaal. Een Pi
heeft geen klokbatterij en gebruikt bij het opstarten de laatst bekende tijd, tot hij de juiste tijd van
internet haalt.

## Wat wordt er getest

| Test                      | Wat het opspoort                                   |
| ------------------------- | -------------------------------------------------- |
| Bord & geheugengrootte    | RAM dat niet (volledig) herkend wordt              |
| Ethernet                  | defecte poort, geen gigabit, geen internet         |
| Wifi                      | defecte wifi-chip of antenne                       |
| Bluetooth                 | ontbrekende adapter                                |
| USB-poorten               | lijst van herkende apparaten                       |
| Opslag schrijven/lezen    | datacorruptie, trage of foutieve SD/NVMe           |
| RAM-geheugentest          | defecte geheugencellen                             |
| CPU-belasting             | crashes onder belasting, oververhitting            |
| Voeding & throttling      | onderspanning, throttling (ook tijdens stresstest) |
| GPIO-loopback (optioneel) | defecte GPIO-pinnen                                |

## Instellen

Pas `pitest.conf` op de bootpartitie aan, gewoon vanaf je pc. Daar stel je de duur van
de stresstest, de hoeveelheid RAM-test en optioneel GPIO-pinparen in. Voor GPIO verbind
je twee pinnen met een jumperdraadje, bv. GPIO17 met GPIO27 → `gpio_pairs = 17-27`.

## Goed om te weten

- Een **FOUT** bij opslag kan ook aan de SD-kaart liggen in plaats van aan de Pi.
  Test bij twijfel met een tweede kaart.
- "Onderspanning" bijna altijd: de voeding of kabel, niet de Pi.
- Een Pi 4 of 5 zonder koeler wordt tijdens de stresstest warm; een **LET OP** voor
  temperatuur is dan normaal, geen defect.
- De USB-test toont wat herkend wordt; controleer zelf of elke stick die je insteekt
  in de lijst staat.

## Zelf de image bouwen

Alleen nodig als je de code aanpast. Zo is `pitest.img.xz` gemaakt:

1. Flash **Raspberry Pi OS Lite (64-bit)** met Raspberry Pi Imager, met deze instellingen:
   hostname `pi-tester`, gebruiker `pitest` / `pitest`, land `BE`, **SSH aan** met wachtwoord,
   geen wifi, geen Raspberry Pi Connect.
   Gebruik een **kleine kaart** (8 of 16 GB): het lezen in stap 5 gaat dan sneller.
2. Start een Pi met die kaart en een netwerkkabel. Kopieer deze map erheen en installeer
   (vanuit Windows met PowerShell):

   ```bash
   scp -r pi-hardwaretest pitest@pi-tester.local:
   ssh pitest@pi-tester.local
   cd pi-hardwaretest
   sudo bash install.sh
   ```

   Gebruik `sudo bash install.sh`: na kopiëren vanaf Windows is het bestand niet meer uitvoerbaar.
3. Test of alles werkt met `sudo systemctl start pitest` en `journalctl -fu pitest`.
4. Ruim op en sluit af:

   ```bash
   sudo rm -f /boot/firmware/testrapport-*.txt /boot/firmware/pitest-overzicht.csv
   rm -rf ~/pi-hardwaretest
   sudo shutdown -h now
   ```

5. Lees de kaart in Windows uit met **Win32 Disk Imager**: kies een bestand `pitest.img`,
   kies de kaart en klik **Lezen** (niet Schrijven!). Vraagt Windows om de kaart te formatteren:
   **Annuleren**.
6. Verklein en pak in met [PiShrink](https://github.com/Drewsif/PiShrink) in WSL (Ubuntu, niet de
   `docker-desktop`-omgeving):

   ```bash
   sudo apt install -y parted xz-utils
   wget https://raw.githubusercontent.com/Drewsif/PiShrink/master/pishrink.sh
   chmod +x pishrink.sh && sudo mv pishrink.sh /usr/local/bin/
   sudo pishrink.sh -Z -a /mnt/d/pad/naar/pitest.img
   ```

   Resultaat: `pitest.img.xz` (van 30 GB naar ±1,4 GB). Zet dat bestand in een nieuwe Release.

## Code-structuur

```txt
pitest/
  core/       basisklassen: Check, CheckResult, Shell, Config
  hardware/   bordinfo, vcgencmd, status-led
  checks/     één bestand per hardwareonderdeel
  report/     tekstrapport en CSV-overzicht
  suite.py    voert de tests uit en bepaalt het eindoordeel
```

Een test toevoegen: maak een subklasse van `Check` in `checks/` en voeg hem toe in
`build_checks()` in `__main__.py`.
