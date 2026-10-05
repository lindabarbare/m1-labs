"""Iesniegumu glabātuve: SQLite datubāze atmiņā.

Pēc restarta dati atgriežas sākuma stāvoklī ar 13 sintētiskiem iesniegumiem.
"""

import sqlite3
import threading

COLUMNS = (
    "id",
    "personalCode",
    "fullName",
    "email",
    "preferredChannel",
    "topic",
    "subject",
    "body",
    "status",
    "receivedAt",
    "dueDate",
    "replyChannel",
    "reasonCode",
)

# Sintētiski dati. Personas kodi neatbilst reālām personām.
SEED = (
    {
        "personalCode": "32000000101",
        "fullName": "Jānis Bērziņš",
        "email": "janis.berzins@example.com",
        "preferredChannel": "EMAIL",
        "topic": "ROADS",
        "subject": "Bedre Ezera ielā",
        "body": "Ezera ielā pie 12. mājas ir dziļa bedre. Lūdzu, salabojiet to.",
        "status": "RECEIVED",
        "receivedAt": "2026-10-01T09:15:00+00:00",
        "dueDate": "2026-11-02",
        "replyChannel": "EMAIL",
        "reasonCode": None,
    },
    {
        "personalCode": "32000000102",
        "fullName": "Līga Ozoliņa-Kalniņa",
        "email": "liga.ozolina@example.com",
        "preferredChannel": "POST",
        "topic": "PLANNING",
        "subject": "Bojāta uzbrauktuve pie bibliotēkas",
        "body": (
            "Es pārvietojos ratiņkrēslā, un uzbrauktuve pie bibliotēkas ir bojāta. "
            "Lūdzu, salabojiet to."
        ),
        "status": "IN_PROGRESS",
        "receivedAt": "2026-08-20T10:00:00+00:00",
        "dueDate": "2026-09-21",
        "replyChannel": "POST",
        "reasonCode": None,
    },
    {
        "personalCode": "32000000103",
        "fullName": "Ņikita Šķēle",
        "email": "nikita.skele@example.com",
        "preferredChannel": "E_ADDRESS",
        "topic": "WASTE",
        "subject": "Atkritumu konteiners netiek iztukšots",
        "body": "Konteiners Liepu ielā 3 nav iztukšots divas nedēļas.",
        "status": "ANSWERED",
        "receivedAt": "2026-09-01T08:30:00+00:00",
        "dueDate": "2026-10-01",
        "replyChannel": "E_ADDRESS",
        "reasonCode": None,
    },
    {
        "personalCode": "32000000104",
        "fullName": "Anna Kalniņa",
        "email": "anna.kalnina@example.com",
        "preferredChannel": "EMAIL",
        "topic": "PARKS",
        "subject": "Salauzts sols parkā",
        "body": "Ezermalas parkā pie strūklakas ir salauzts sols.",
        "status": "RECEIVED",
        "receivedAt": "2026-10-02T07:45:00+00:00",
        "dueDate": "2026-11-01",
        "replyChannel": "EMAIL",
        "reasonCode": None,
    },
    {
        "personalCode": "32000000105",
        "fullName": "Pēteris Liepiņš",
        "email": "peteris.liepins@example.com",
        "preferredChannel": "POST",
        "topic": "ROADS",
        "subject": "Neapgaismota iela",
        "body": "Bērzu ielā nedeg ielu apgaismojums jau nedēļu.",
        "status": "IN_PROGRESS",
        "receivedAt": "2026-09-15T12:00:00+00:00",
        "dueDate": "2026-10-15",
        "replyChannel": "POST",
        "reasonCode": None,
    },
    {
        "personalCode": "32000000106",
        "fullName": "Elīna Zariņa",
        "email": "elina.zarina@example.com",
        "preferredChannel": "E_ADDRESS",
        "topic": "WASTE",
        "subject": "Nelegāla izgāztuve mežmalā",
        "body": "Mežmalā aiz Priežu ielas kāds izgāž būvgružus.",
        "status": "FORWARDED",
        "receivedAt": "2026-09-10T14:20:00+00:00",
        "dueDate": "2026-10-12",
        "replyChannel": "E_ADDRESS",
        "reasonCode": None,
    },
    {
        "personalCode": "32000000107",
        "fullName": "Mārtiņš Ozols",
        "email": "martins.ozols@example.com",
        "preferredChannel": "EMAIL",
        "topic": "PLANNING",
        "subject": "Jautājums par detālplānojumu",
        "body": "Kad būs pieejams Ezera krasta detālplānojuma projekts?",
        "status": "ANSWERED",
        "receivedAt": "2026-08-05T09:00:00+00:00",
        "dueDate": "2026-09-04",
        "replyChannel": "EMAIL",
        "reasonCode": None,
    },
    {
        "personalCode": "32000000108",
        "fullName": "Ilze Krūmiņa",
        "email": "ilze.krumina@example.com",
        "preferredChannel": "EMAIL",
        "topic": "OTHER",
        "subject": "Bibliotēkas darba laiks",
        "body": "Lūdzu, pagariniet bibliotēkas darba laiku sestdienās.",
        "status": "WITHDRAWN",
        "receivedAt": "2026-09-03T16:10:00+00:00",
        "dueDate": "2026-10-05",
        "replyChannel": "EMAIL",
        "reasonCode": None,
    },
    {
        "personalCode": "32000000109",
        "fullName": "Kārlis Vītols",
        "email": "karlis.vitols@example.com",
        "preferredChannel": "POST",
        "topic": "PARKS",
        "subject": "Rotaļu laukuma šūpoles",
        "body": "Rotaļu laukumā Skolas ielā ir bojātas šūpoles.",
        "status": "RECEIVED",
        "receivedAt": "2026-10-03T08:05:00+00:00",
        "dueDate": "2026-11-02",
        "replyChannel": "POST",
        "reasonCode": None,
    },
    {
        "personalCode": "32000000110",
        "fullName": "Dace Strautiņa",
        "email": "dace.strautina@example.com",
        "preferredChannel": "E_ADDRESS",
        "topic": "ROADS",
        "subject": "Trūkst gājēju pārejas",
        "body": "Pie skolas Ezera ielā vajadzīga gājēju pāreja.",
        "status": "IN_PROGRESS",
        "receivedAt": "2026-09-22T10:30:00+00:00",
        "dueDate": "2026-10-22",
        "replyChannel": "E_ADDRESS",
        "reasonCode": None,
    },
    {
        "personalCode": "32000000111",
        "fullName": "Roberts Kļaviņš",
        "email": "roberts.klavins@example.com",
        "preferredChannel": "EMAIL",
        "topic": "WASTE",
        "subject": "Šķirošanas konteineri",
        "body": "Lūdzu, uzstādiet stikla konteineru Ābeļu ielā.",
        "status": "RECEIVED",
        "receivedAt": "2026-10-04T11:40:00+00:00",
        "dueDate": "2026-11-03",
        "replyChannel": "EMAIL",
        "reasonCode": None,
    },
    {
        "personalCode": "32000000112",
        "fullName": "Zane Āboliņa",
        "email": "zane.abolina@example.com",
        "preferredChannel": "POST",
        "topic": "PLANNING",
        "subject": "Būvatļauja šķūnim",
        "body": "Vai šķūņa būvei savā zemesgabalā vajag būvatļauju?",
        "status": "ANSWERED",
        "receivedAt": "2026-08-25T13:15:00+00:00",
        "dueDate": "2026-09-24",
        "replyChannel": "POST",
        "reasonCode": None,
    },
    {
        "personalCode": "32000000113",
        "fullName": "Gints Bērziņš",
        "email": "gints.berzins@example.com",
        "preferredChannel": "E_ADDRESS",
        "topic": "OTHER",
        "subject": "Sporta zāles noma",
        "body": "Kā var nomāt skolas sporta zāli vakaros?",
        "status": "RECEIVED",
        "receivedAt": "2026-10-05T06:55:00+00:00",
        "dueDate": "2026-11-04",
        "replyChannel": "E_ADDRESS",
        "reasonCode": None,
    },
)

_INSERT = """
    INSERT INTO submissions (
        id, personalCode, fullName, email, preferredChannel, topic, subject, body,
        status, receivedAt, dueDate, replyChannel, reasonCode
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
"""

_lock = threading.Lock()
_conn: sqlite3.Connection | None = None


def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(":memory:", check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute(
        """
        CREATE TABLE submissions (
            seq INTEGER PRIMARY KEY AUTOINCREMENT,
            id TEXT UNIQUE NOT NULL,
            personalCode TEXT NOT NULL,
            fullName TEXT NOT NULL,
            email TEXT NOT NULL,
            preferredChannel TEXT NOT NULL,
            topic TEXT NOT NULL,
            subject TEXT NOT NULL,
            body TEXT NOT NULL,
            status TEXT NOT NULL,
            receivedAt TEXT NOT NULL,
            dueDate TEXT NOT NULL,
            replyChannel TEXT NOT NULL,
            reasonCode TEXT
        )
        """
    )
    return conn


def reset(seed: bool = True) -> None:
    global _conn
    with _lock:
        _conn = _connect()
    if seed:
        for record in SEED:
            add(record)


def add(data: dict) -> dict:
    with _lock:
        (seq,) = _conn.execute(
            "SELECT COALESCE(MAX(seq), 0) + 1 FROM submissions"
        ).fetchone()
        record = {**data, "id": f"IES-2026-{seq:06d}"}
        _conn.execute(_INSERT, [record.get(column) for column in COLUMNS])
    return record


def get(submission_id: str) -> dict | None:
    with _lock:
        row = _conn.execute(
            "SELECT * FROM submissions WHERE id = ?", (submission_id,)
        ).fetchone()
    if row is None:
        return None
    return {column: row[column] for column in COLUMNS}
