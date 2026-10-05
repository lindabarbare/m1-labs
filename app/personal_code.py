"""Personas koda pārbaude (CR-1).

Formāts: 11 cipari vai DDMMGG-NNNNN (defise pēc 6. cipara).
- jaunais kods sākas ar 32: datuma un kontrolcipara nav;
- vecais kods: DDMMGG ir īsts datums, 7. cipars ir gadsimts
  (0 = 1800, 1 = 1900, 2 = 2000), datums nav vēlāks par šodienu Latvijas laikā.
Kontrolciparu nepārbauda. Saglabā 11 ciparus bez defises.
"""

import re
from datetime import date, datetime, timezone
from zoneinfo import ZoneInfo

# [0-9], nevis \d: \d atbilst arī citu rakstu cipariem, piemēram, "٣".
_PATTERN = re.compile(r"^[0-9]{6}-?[0-9]{5}$")
_CENTURIES = {"0": 1800, "1": 1900, "2": 2000}
_TIMEZONE = ZoneInfo("Europe/Riga")


class InvalidPersonalCode(ValueError):
    pass


def _today(now: datetime | None = None) -> date:
    """Šodienas datums Latvijas laikā."""
    now = now or datetime.now(timezone.utc)
    return now.astimezone(_TIMEZONE).date()


def normalize(value: str) -> str:
    """Atgriež personas kodu 11 ciparu formā vai izmet InvalidPersonalCode."""
    value = value.strip()
    if not _PATTERN.match(value):
        raise InvalidPersonalCode("format")
    digits = value.replace("-", "")
    if digits.startswith("32"):
        return digits
    birth_date = _birth_date(digits)
    if birth_date is None:
        raise InvalidPersonalCode("date")
    if birth_date > _today():
        raise InvalidPersonalCode("future")
    return digits


def _birth_date(digits: str) -> date | None:
    century = _CENTURIES.get(digits[6])
    if century is None:
        return None
    try:
        return date(century + int(digits[4:6]), int(digits[2:4]), int(digits[0:2]))
    except ValueError:
        return None
