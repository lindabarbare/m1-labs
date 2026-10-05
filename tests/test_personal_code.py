"""CR-1: personas koda pārbaude.

Vecā formāta derīgie kodi ir ar gadsimta ciparu 0 (1800. gadi), tāpēc nevar
piederēt dzīvai personai. Nederīgajiem kodiem kontrolcipars ir pareizs, lai
tests pārbaudītu tieši datuma kļūdu.
"""

import pytest

from app import storage

VALID_OLD = "150385-00003"  # 15.03.1885
VALID_OLD_LEAP = "290288-00018"  # 29.02.1888, garais gads


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
        ("  32000000001 ", "32000000001"),  # 3
        (" 320000-00001\t", "32000000001"),  # 3
        (VALID_OLD, "15038500003"),  # 4
        ("15038500003", "15038500003"),  # 4
        (VALID_OLD_LEAP, "29028800018"),  # 5
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
    "code",
    [
        "310285-00018",  # 31.02.
        "290289-00000",  # 29.02.1889, nav garais gads
        "290200-10003",  # 29.02.1900, nav garais gads
        "150385-50000",  # gadsimta cipars 5 nav derīgs
    ],
)
def test_invalid_date_is_rejected(client, valid_payload, fake_omd, code):  # 6
    assert_rejected(post_code(client, valid_payload, code), fake_omd, "INVALID_FORMAT")


def test_wrong_checksum_is_rejected(client, valid_payload, fake_omd):  # 7
    response = post_code(client, valid_payload, "150385-00004")
    assert_rejected(response, fake_omd, "INVALID_FORMAT")


@pytest.mark.parametrize(
    "code",
    [
        "32000000A01",  # burts
        "3200000001",  # 10 cipari
        "320000000001",  # 12 cipari
        "3200-0000001",  # defise nepareizā vietā
        "320000--00001",  # divas defises
        "320000 00001",  # atstarpe vidū
        "320000-00001-",
    ],
)
def test_wrong_format_is_rejected(client, valid_payload, fake_omd, code):  # 8
    assert_rejected(post_code(client, valid_payload, code), fake_omd, "INVALID_FORMAT")


def test_number_instead_of_string_is_rejected(client, valid_payload, fake_omd):  # 8
    response = post_code(client, valid_payload, 32000000001)
    assert_rejected(response, fake_omd, "INVALID_FORMAT")


@pytest.mark.parametrize("code", ["", "   "])
def test_empty_code_is_required(client, valid_payload, fake_omd, code):  # 9
    assert_rejected(post_code(client, valid_payload, code), fake_omd, "REQUIRED")


def test_missing_code_is_required(client, valid_payload, fake_omd):  # 9
    del valid_payload["personalCode"]
    response = client.post("/submissions", json=valid_payload)
    assert_rejected(response, fake_omd, "REQUIRED")


def test_error_does_not_echo_personal_code(client, valid_payload):
    response = post_code(client, valid_payload, "150385-00004")
    assert "150385" not in response.text


def test_seed_has_13_submissions_with_valid_codes():
    from app.models import SubmissionCreate

    storage.reset()
    codes = [storage.get(f"IES-2026-{n:06d}")["personalCode"] for n in range(1, 14)]
    assert storage.get("IES-2026-000014") is None
    assert all(code.startswith("32") for code in codes[3:])
    for record in storage.SEED:
        SubmissionCreate(**record)
