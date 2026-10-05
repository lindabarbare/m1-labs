"""CR-1: personas koda pārbaude. Komentārā pieņemšanas kritērija numurs.

Pārbauda tikai formātu, ne datumu un kontrolciparu. Visi kodi ir sintētiski.
"""

import logging

import pytest

from app import storage


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
        ("311299-21233", "31129921233"),  # 8
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


@pytest.mark.parametrize(
    ("code", "stored"),
    [
        ("310285-00019", "31028500019"),  # 31.02. neeksistē
        ("15038500004", "15038500004"),  # nepareizs kontrolcipars
    ],
)
def test_date_and_checksum_are_not_checked(client, valid_payload, code, stored):
    # Precizējums: tikai formāts. Ārpus tvēruma: datums un kontrolcipars.
    response = post_code(client, valid_payload, code)
    assert response.status_code == 201
    saved = client.get(f"/submissions/{response.json()['id']}").json()
    assert saved["personalCode"] == stored


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
