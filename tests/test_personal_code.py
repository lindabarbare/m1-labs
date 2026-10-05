"""CR-1: personas koda pārbaude. Komentārā pieņemšanas kritērija numurs.

Vecajiem kodiem pārbauda datumu, ne kontrolciparu. Visi kodi ir sintētiski:
derīgajiem vecā formāta kodiem ir gadsimta cipars 0 (1800. gadi).
"""

import logging
from datetime import date, datetime, timezone

import pytest

from app import personal_code, storage


def post_code(client, payload, code):
    payload["personalCode"] = code
    return client.post("/submissions", json=payload)


def assert_rejected(response, fake_omd, issue):
    assert response.status_code == 400
    error = response.json()["error"]
    assert error["code"] == "VALIDATION_ERROR"
    assert {"field": "personalCode", "issue": issue} in error["details"]
    assert fake_omd.calls == []
    assert storage.get("IES-2026-000001") is None


@pytest.mark.parametrize(
    ("code", "stored"),
    [
        ("32000000001", "32000000001"),  # 1
        ("320000-00001", "32000000001"),  # 2
        (" 32000000001 ", "32000000001"),  # 3
        (" 320000-00001\t", "32000000001"),  # 3
        ("290288-00000", "29028800000"),  # 12: 29.02.1888, garais gads
        ("150385-00003", "15038500003"),  # 15
        ("15038500003", "15038500003"),  # 15 bez defises
    ],
)
def test_valid_code_is_accepted_and_stored_normalized(
    client, valid_payload, fake_omd, code, stored
):
    response = post_code(client, valid_payload, code)
    assert response.status_code == 201
    saved = client.get(f"/submissions/{response.json()['id']}").json()
    assert saved["personalCode"] == stored
    assert fake_omd.calls == [stored]


def test_checksum_is_not_checked(client, valid_payload):
    # Ārpus tvēruma: kontrolcipars. 150385-00003 ar citu pēdējo ciparu.
    response = post_code(client, valid_payload, "150385-00004")
    assert response.status_code == 201


@pytest.mark.parametrize(
    "code",
    [
        "311299-21233",  # 8: 31.12.2099, nākotnē
        "092089-10078",  # 10: 20. mēnesis
        "290200-10000",  # 11: 29.02.1900, nav garais gads
        "150385-50000",  # 13: gadsimta cipars 5
        "00000010000",  # 14: sākas ar 00
        "310285-00000",  # 31.02.
        "000385-00000",  # 0. diena
        "150085-00000",  # 0. mēnesis
        "330385-00000",  # sākas ar 33
        "990385-00000",  # sākas ar 99
        "150385-30000",  # gadsimta cipars 3
        "150385-90000",  # gadsimta cipars 9
    ],
)
def test_invalid_date_is_rejected(client, valid_payload, fake_omd, code):
    assert_rejected(post_code(client, valid_payload, code), fake_omd, "INVALID_FORMAT")


@pytest.fixture
def today_15_03_1885(monkeypatch):
    # Fiksēta "šodiena" 1800. gados, lai robežgadījumu kodi paliktu sintētiski.
    monkeypatch.setattr(personal_code, "_today", lambda: date(1885, 3, 15))


def test_born_today_is_accepted(client, valid_payload, today_15_03_1885):
    assert post_code(client, valid_payload, "150385-00003").status_code == 201


def test_born_tomorrow_is_rejected(client, valid_payload, fake_omd, today_15_03_1885):
    response = post_code(client, valid_payload, "160385-00003")
    assert_rejected(response, fake_omd, "INVALID_FORMAT")


def test_today_is_latvian_date():
    # 2026-10-04 22:30 UTC Rīgā jau ir 2026-10-05 01:30.
    now = datetime(2026, 10, 4, 22, 30, tzinfo=timezone.utc)
    assert personal_code._today(now) == date(2026, 10, 5)


@pytest.mark.parametrize(
    "code",
    [
        "3200000000",  # 4: 10 cipari
        "320000000012",  # 5: 12 cipari
        "32000000O01",  # 6: burts O
        "3200-0000001",  # 9: defise nepareizā vietā
        "320000--00001",  # divas defises
        "320000 00001",  # atstarpe vidū
        "320000-00001-",  # defise beigās
        "3200000000٣",  # arābu cipars 3
    ],
)
def test_wrong_format_is_rejected(client, valid_payload, fake_omd, code):
    assert_rejected(post_code(client, valid_payload, code), fake_omd, "INVALID_FORMAT")


def test_number_instead_of_string_is_rejected(client, valid_payload, fake_omd):
    response = post_code(client, valid_payload, 32000000001)
    assert_rejected(response, fake_omd, "INVALID_FORMAT")


def test_missing_code_is_required(client, valid_payload, fake_omd):  # 7
    del valid_payload["personalCode"]
    response = client.post("/submissions", json=valid_payload)
    assert_rejected(response, fake_omd, "REQUIRED")


@pytest.mark.parametrize("code", ["", "   ", None])
def test_empty_code_is_required(client, valid_payload, fake_omd, code):  # 7
    assert_rejected(post_code(client, valid_payload, code), fake_omd, "REQUIRED")


def test_error_does_not_echo_personal_code(client, valid_payload, caplog):
    caplog.set_level(logging.DEBUG)
    response = post_code(client, valid_payload, "320000-0000X")
    assert "0000X" not in response.text
    assert "0000X" not in caplog.text


def test_log_has_id_but_not_personal_code(client, valid_payload, caplog):
    caplog.set_level(logging.DEBUG)
    response = post_code(client, valid_payload, "32000000001")
    assert response.json()["id"] in caplog.text
    assert "32000000001" not in caplog.text
    assert valid_payload["body"] not in caplog.text
