"""CR-1: personas koda pārbaude (POST /submissions, lauks personalCode).

Katram pieņemšanas kritērijam (tracker/CR-1.md, rindas 1–15) tieši viens tests.
Sagaidāmās vērtības ņemtas no kritērijiem un sadaļas "Precizējumi".
Kļūdas forma pēc docs/openapi.yaml (Error, responses.ValidationError).
Visi kodi ir sintētiski.
"""


def post_code(client, payload, code):
    payload["personalCode"] = code
    return client.post("/submissions", json=payload)


def assert_contract_error(response, issue, sent_code=None):
    """400 pēc līguma kļūdu shēmas; ziņojumā nav ievadītā koda (Precizējumi)."""
    assert response.status_code == 400
    body = response.json()
    error = body["error"]
    assert error["code"] == "VALIDATION_ERROR"
    assert isinstance(error["message"], str)
    assert isinstance(error["details"], list)
    for item in error["details"]:
        assert isinstance(item["field"], str)
        assert item["issue"] in ("REQUIRED", "INVALID_FORMAT", "TOO_LONG")
    assert {"field": "personalCode", "issue": issue} in error["details"]
    if sent_code is not None and sent_code.strip():
        assert sent_code not in response.text
        assert sent_code.strip() not in response.text


def assert_saved(client, response, stored):
    """201 un saglabātā vērtība, nolasīta ar GET /submissions/{id} (līgums: Submission)."""
    assert response.status_code == 201
    saved = client.get(f"/submissions/{response.json()['id']}")
    assert saved.status_code == 200
    assert saved.json()["personalCode"] == stored


def test_cr1_ac1_eleven_digits_saved(client, valid_payload):
    response = post_code(client, valid_payload, "32000000001")
    assert_saved(client, response, "32000000001")


def test_cr1_ac2_hyphen_normalised(client, valid_payload):
    response = post_code(client, valid_payload, "320000-00001")
    assert_saved(client, response, "32000000001")


def test_cr1_ac3_surrounding_spaces_accepted(client, valid_payload):
    # Kritērijs prasa tikai 201. Sagaidāms, ka saglabāts 32000000001,
    # bet saglabātā vērtība kritērijā nav norādīta, tāpēc to nepārbauda.
    response = post_code(client, valid_payload, " 32000000001 ")
    assert response.status_code == 201


def test_cr1_ac4_ten_digits_invalid_format(client, valid_payload):
    code = "3200000000"
    assert_contract_error(
        post_code(client, valid_payload, code), "INVALID_FORMAT", code
    )


def test_cr1_ac5_twelve_digits_invalid_format(client, valid_payload):
    code = "320000000012"
    assert_contract_error(
        post_code(client, valid_payload, code), "INVALID_FORMAT", code
    )


def test_cr1_ac6_letter_o_invalid_format(client, valid_payload):
    code = "32000000O01"
    assert_contract_error(
        post_code(client, valid_payload, code), "INVALID_FORMAT", code
    )


def test_cr1_ac7_missing_field_required(client, valid_payload):
    del valid_payload["personalCode"]
    response = client.post("/submissions", json=valid_payload)
    assert_contract_error(response, "REQUIRED")


def test_cr1_ac8_future_birth_date_invalid_format(client, valid_payload):
    # 31.12.2099 ir nākotnē attiecībā pret jebkuru reālu šodienu (Latvijas laiks).
    code = "311299-21233"
    assert_contract_error(
        post_code(client, valid_payload, code), "INVALID_FORMAT", code
    )


def test_cr1_ac9_hyphen_wrong_position_invalid_format(client, valid_payload):
    code = "3200-0000001"
    assert_contract_error(
        post_code(client, valid_payload, code), "INVALID_FORMAT", code
    )


def test_cr1_ac10_month_20_invalid_format(client, valid_payload):
    code = "092089-10078"
    assert_contract_error(
        post_code(client, valid_payload, code), "INVALID_FORMAT", code
    )


def test_cr1_ac11_feb29_1900_invalid_format(client, valid_payload):
    code = "290200-10000"
    assert_contract_error(
        post_code(client, valid_payload, code), "INVALID_FORMAT", code
    )


def test_cr1_ac12_feb29_1888_leap_year_saved(client, valid_payload):
    response = post_code(client, valid_payload, "290288-00000")
    assert_saved(client, response, "29028800000")


def test_cr1_ac13_century_digit_5_invalid_format(client, valid_payload):
    code = "150385-50000"
    assert_contract_error(
        post_code(client, valid_payload, code), "INVALID_FORMAT", code
    )


def test_cr1_ac14_starts_with_00_invalid_format(client, valid_payload):
    code = "00000010000"
    assert_contract_error(
        post_code(client, valid_payload, code), "INVALID_FORMAT", code
    )


def test_cr1_ac15_old_format_1885_saved(client, valid_payload):
    response = post_code(client, valid_payload, "150385-00003")
    assert_saved(client, response, "15038500003")
