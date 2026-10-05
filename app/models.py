"""Datu modeļi pēc API līguma (API contract) docs/openapi.yaml."""

from datetime import date, datetime
from enum import Enum

from pydantic import BaseModel, field_validator
from pydantic_core import PydanticCustomError

from app import personal_code


class PreferredChannel(str, Enum):
    EMAIL = "EMAIL"
    POST = "POST"
    E_ADDRESS = "E_ADDRESS"


class ReplyChannel(str, Enum):
    EMAIL = "EMAIL"
    POST = "POST"
    E_ADDRESS = "E_ADDRESS"


class Topic(str, Enum):
    ROADS = "ROADS"
    WASTE = "WASTE"
    PLANNING = "PLANNING"
    PARKS = "PARKS"
    OTHER = "OTHER"


# Tēmu nosaukumi pēc līguma. Secība sakrīt ar Topic secību, OTHER vienmēr beigās.
TOPIC_NAMES: dict[Topic, str] = {
    Topic.ROADS: "Ceļi un ielas",
    Topic.WASTE: "Atkritumi",
    Topic.PLANNING: "Teritorijas plānošana",
    Topic.PARKS: "Parki un skvēri",
    Topic.OTHER: "Cits",
}


class TopicItem(BaseModel):
    code: Topic
    name: str


class SubmissionStatus(str, Enum):
    RECEIVED = "RECEIVED"
    IN_PROGRESS = "IN_PROGRESS"
    FORWARDED = "FORWARDED"
    ANSWERED = "ANSWERED"
    WITHDRAWN = "WITHDRAWN"


class SubmissionCreate(BaseModel):
    personalCode: str
    fullName: str
    email: str  # TODO: pārbaudīt e-pasta formātu
    preferredChannel: PreferredChannel
    topic: Topic
    subject: str
    body: str

    @field_validator("personalCode", mode="before")
    @classmethod
    def check_personal_code(cls, value):
        # Kļūdas tekstā ievadīto vērtību neatkārtojam: tie ir personas dati.
        if value is None or (isinstance(value, str) and not value.strip()):
            raise PydanticCustomError("missing", "Personas kods nav ievadīts")
        if not isinstance(value, str):
            return value  # str pārbaude atgriezīs INVALID_FORMAT
        try:
            return personal_code.normalize(value)
        except personal_code.InvalidPersonalCode:
            raise PydanticCustomError(
                "personal_code_invalid", "Personas kods nav derīgs"
            ) from None


class SubmissionCreated(BaseModel):
    id: str
    status: SubmissionStatus
    receivedAt: datetime
    dueDate: date
    replyChannel: ReplyChannel
    reasonCode: str | None = None


class Submission(SubmissionCreated, SubmissionCreate):
    pass


class SubmissionListItem(BaseModel):
    # CR-3: tikai līgumā noteiktie lauki, bez personas datiem un iesnieguma teksta.
    id: str
    status: SubmissionStatus
    topic: Topic
    receivedAt: datetime
    dueDate: date
    replyChannel: ReplyChannel


class Health(BaseModel):
    status: str
    version: str


class ErrorDetail(BaseModel):
    field: str
    issue: str


class ErrorBody(BaseModel):
    code: str
    message: str
    details: list[ErrorDetail] | None = None


class Error(BaseModel):
    error: ErrorBody
