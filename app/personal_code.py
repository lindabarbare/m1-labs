"""Personas koda pārbaude (CR-1).

Pārbauda tikai formātu: 11 cipari vai DDMMGG-NNNNN (defise pēc 6. cipara).
Datumu un kontrolciparu nepārbauda. Saglabā 11 ciparus bez defises.
"""

import re

# [0-9], nevis \d: \d atbilst arī citu rakstu cipariem, piemēram, "٣".
_PATTERN = re.compile(r"^[0-9]{6}-?[0-9]{5}$")


class InvalidPersonalCode(ValueError):
    pass


def normalize(value: str) -> str:
    """Atgriež personas kodu 11 ciparu formā vai izmet InvalidPersonalCode."""
    value = value.strip()
    if not _PATTERN.match(value):
        raise InvalidPersonalCode("format")
    return value.replace("-", "")
