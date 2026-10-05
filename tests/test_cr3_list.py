"""CR-3: iesniegumu saraksts darbiniekam (pieņemšanas kritēriji 1-5)."""

from app import storage

LIST_FIELDS = {"id", "status", "topic", "receivedAt", "dueDate", "replyChannel"}


def test_ac1_filter_by_status(client):
    storage.reset()
    response = client.get("/submissions?status=RECEIVED")
    assert response.status_code == 200
    items = response.json()
    assert items
    assert all(item["status"] == "RECEIVED" for item in items)


def test_ac2_filter_by_topic(client):
    storage.reset()
    response = client.get("/submissions?topic=ROADS")
    assert response.status_code == 200
    items = response.json()
    assert items
    assert all(item["topic"] == "ROADS" for item in items)


def test_ac3_both_filters(client):
    storage.reset()
    response = client.get("/submissions?status=RECEIVED&topic=ROADS")
    assert response.status_code == 200
    items = response.json()
    assert items
    assert all(
        item["status"] == "RECEIVED" and item["topic"] == "ROADS" for item in items
    )
    assert client.get("/submissions?status=RECEIVED&topic=WASTE").json() == []


def test_ac4_unknown_status_is_validation_error(client):
    storage.reset()
    response = client.get("/submissions?status=DONE")
    assert response.status_code == 400
    error = response.json()["error"]
    assert error["code"] == "VALIDATION_ERROR"
    assert {"field": "status", "issue": "INVALID_FORMAT"} in error["details"]


def test_ac5_list_has_only_contract_fields(client):
    storage.reset()
    items = client.get("/submissions").json()
    assert len(items) == 3
    assert all(set(item) == LIST_FIELDS for item in items)


# Regresija: filtra vērtība nonāca SQL tekstā (SQL injekcija).
def test_status_injection_is_rejected(client):
    storage.reset()
    response = client.get("/submissions", params={"status": "x' OR '1'='1"})
    assert response.status_code == 400
    assert response.json()["error"]["details"][0]["field"] == "status"


def test_topic_injection_is_rejected(client):
    storage.reset()
    response = client.get("/submissions", params={"topic": "x' OR '1'='1"})
    assert response.status_code == 400
    assert response.json()["error"]["details"][0]["field"] == "topic"


def test_storage_filter_is_parameterized():
    storage.reset()
    assert storage.list_submissions(status="x' OR '1'='1") == []
    assert storage.list_submissions(topic="x' OR '1'='1") == []
