"""Personas koda pārbaude (CR-1).

Der divi formāti, ievadē ar defisi pēc 6. cipara vai bez tās:
- jaunais: sākas ar 32, kopā 11 cipari;
- vecais: DDMMGG + gadsimta cipars (0 = 1800, 1 = 1900, 2 = 2000) + 4 cipari,
  datumam jābūt īstam, pēdējais cipars ir kontrolcipars.
Saglabā 11 ciparus bez defises.
"""

import re
from datetime import date

_PATTERN = re.compile(r"^\d{6}-?\d{5}$")
_WEIGHTS = (1, 6, 3, 7, 9, 10, 5, 8, 4, 2)
_CENTURIES = {"0": 1800, "1": 1900, "2": 2000}


class InvalidPersonalCode(ValueError):
    pass


def normalize(value: str) -> str:
    """Atgriež personas kodu 11 ciparu formā vai izmet InvalidPersonalCode."""
    value = value.strip()
    if not _PATTERN.match(value):
        raise InvalidPersonalCode("format")
    digits = value.replace("-", "")
    if digits.startswith("32"):
        return digits
    if not _is_real_date(digits):
        raise InvalidPersonalCode("date")
    if not _checksum_ok(digits):
        raise InvalidPersonalCode("checksum")
    return digits


def _is_real_date(digits: str) -> bool:
    century = _CENTURIES.get(digits[6])
    if century is None:
        return False
    try:
        date(century + int(digits[4:6]), int(digits[2:4]), int(digits[0:2]))
    except ValueError:
        return False
    return True


def _checksum_ok(digits: str) -> bool:
    total = sum(w * int(d) for w, d in zip(_WEIGHTS, digits[:10], strict=True))
    return (1101 - total) % 11 == int(digits[10])
