"""CR-0: tēma PARKS un tēmu saraksts GET /topics."""


def test_list_topics_returns_all_in_order(client):
    # AC1, AC4: esošie kodi un nosaukumi nemainās, OTHER ir beigās
    response = client.get("/topics")
    assert response.status_code == 200
    assert response.json() == [
        {"code": "ROADS", "name": "Ceļi un ielas"},
        {"code": "WASTE", "name": "Atkritumi"},
        {"code": "PLANNING", "name": "Teritorijas plānošana"},
        {"code": "PARKS", "name": "Parki un skvēri"},
        {"code": "OTHER", "name": "Cits"},
    ]


def test_create_submission_with_parks_topic(client, valid_payload):
    # AC2
    valid_payload["topic"] = "PARKS"
    response = client.post("/submissions", json=valid_payload)
    assert response.status_code == 201


def test_unknown_topic_returns_validation_error(client, valid_payload):
    # AC3
    valid_payload["topic"] = "ZOO"
    response = client.post("/submissions", json=valid_payload)
    assert response.status_code == 400
    error = response.json()["error"]
    assert error["code"] == "VALIDATION_ERROR"
    assert [d["field"] for d in error["details"]] == ["topic"]
