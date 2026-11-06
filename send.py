#!/usr/bin/env python3
"""Schickt am Geburtstag die fertige Story per Mail. Läuft täglich in GitHub Actions, unabhängig vom Mac.

  python3 send.py            # heute (Zeitzone Zürich), braucht GMX_PASSWORD
  python3 send.py 23.11      # dieses Datum senden (Test)
  python3 send.py 23.11 --trocken   # nur anzeigen
"""
import datetime
import os
import smtplib
import ssl
import sys
from email.message import EmailMessage
from pathlib import Path
from zoneinfo import ZoneInfo

MAIL = "matti.flueckiger@gmx.ch"
ROOT = Path(__file__).resolve().parent
PROTOKOLL = ROOT / "gesendet.txt"  # "JJJJ-MM-TT Name": mehrere Versuche pro Morgen, aber nur eine Mail


def main():
    args = [a for a in sys.argv[1:] if a != "--trocken"]
    trocken = "--trocken" in sys.argv
    test = bool(args and args[0])
    jetzt = datetime.datetime.now(ZoneInfo("Europe/Zurich"))
    datum = args[0] if test else jetzt.strftime("%d.%m")
    schon = set(PROTOKOLL.read_text(encoding="utf-8").splitlines()) if PROTOKOLL.exists() else set()
    treffer = [z.split(";") for z in (ROOT / "geburtstage.csv").read_text(encoding="utf-8").splitlines()
               if z.startswith(datum + ";")]
    print(f"{datum}: {len(treffer)} Geburtstag(e)")
    for _, name, datei in treffer:
        eintrag = f"{jetzt:%Y-%m-%d} {name}"
        if not test and eintrag in schon:
            print(name, "schon gesendet")
            continue
        bild = ROOT / "stories" / datei
        print(name, datei, "ok" if bild.exists() else "FEHLT")
        if trocken:
            continue
        m = EmailMessage()
        m["Subject"] = f"🎂 Heute Geburtstag: {name} – Story posten"
        m["From"] = m["To"] = MAIL
        m.set_content(f"Heute hat {name} Geburtstag. Die Story ist angehängt, bitte posten.")
        m.add_attachment(bild.read_bytes(), maintype="image", subtype="png", filename=datei)
        with smtplib.SMTP("mail.gmx.net", 587, timeout=60) as s:
            s.starttls(context=ssl.create_default_context())
            s.login(MAIL, os.environ["GMX_PASSWORD"])
            s.send_message(m)
        print("gesendet")
        if not test:
            with PROTOKOLL.open("a", encoding="utf-8") as f:
                f.write(eintrag + "\n")


if __name__ == "__main__":
    main()
