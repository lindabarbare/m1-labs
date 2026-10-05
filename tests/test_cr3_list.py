"""CR-3: iesniegumu saraksts darbiniekam (piegādātāja testi)."""

from app import storage


def test_list_received(client):
    storage.reset()
    response = client.get("/submissions?status=RECEIVED")
    assert response.status_code == 200
    assert all(item["status"] == "RECEIVED" for item in response.json())


def test_list_by_topic(client):
    storage.reset()
    response = client.get("/submissions?topic=ROADS")
    assert response.status_code == 200
    assert all(item["topic"] == "ROADS" for item in response.json())


def test_list_all(client):
    storage.reset()
    response = client.get("/submissions")
    assert response.status_code == 200
    assert len(response.json()) == 3


# Regresija: filtra vērtība nonāca SQL tekstā (SQL injekcija).
def test_unknown_status_is_validation_error(client):
    storage.reset()
    response = client.get("/submissions?status=DONE")
    assert response.status_code == 400
    error = response.json()["error"]
    assert error["code"] == "VALIDATION_ERROR"
    assert {"field": "status", "issue": "INVALID_FORMAT"} in error["details"]


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


def test_status_and_topic_together(client):
    storage.reset()
    response = client.get("/submissions?status=RECEIVED&topic=ROADS")
    assert response.status_code == 200
    assert all(
        item["status"] == "RECEIVED" and item["topic"] == "ROADS"
        for item in response.json()
    )
