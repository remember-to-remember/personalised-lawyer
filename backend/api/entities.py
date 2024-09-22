""" Module for entities. """

from datetime import datetime
from typing import Annotated, List, Optional, Self
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, model_validator
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, declarative_base, mapped_column, relationship
from sqlalchemy.types import DateTime, Enum, Float, LargeBinary, Text, Unicode, Uuid

from backend.api.enum import AttachmentType, InferenceProviderType
from backend.api.lib import now_utc

Base = declarative_base()


class Caller(Base):
    """Class for caller table."""

    __tablename__ = "caller"

    # primary and foreign keys
    caller_id: Mapped[UUID] = mapped_column(Uuid(), default=uuid4, primary_key=True)
    chats: Mapped[Optional[list["Chat"]]] = relationship(
        back_populates="caller", lazy="noload"
    )

    # core fields
    name: Mapped[str] = mapped_column(Unicode(100))
    idp_id: Mapped[str] = mapped_column(Unicode(100), unique=True)
    email: Mapped[str] = mapped_column(Unicode(100), unique=True)

    # time and duration fields
    first_created: Mapped[datetime] = mapped_column(DateTime(), default=now_utc)
    last_updated: Mapped[datetime] = mapped_column(
        DateTime(), default=now_utc, onupdate=now_utc
    )

    @classmethod
    def get_exclude_fields_for_logging(cls) -> set[str]:
        exclude_fields = {"_sa_instance_state"}
        return exclude_fields


class Chat(Base):
    """Class for chat table."""

    __tablename__ = "chat"

    # primary and foreign keys
    chat_id: Mapped[UUID] = mapped_column(Uuid(), default=uuid4, primary_key=True)
    caller_id: Mapped[UUID] = mapped_column(ForeignKey("caller.caller_id"))
    caller: Mapped[Caller] = relationship(back_populates="chats")

    # core fields
    caller_session_id: Mapped[str] = mapped_column(Unicode(50))
    caller_chat_text: Mapped[str] = mapped_column(Text())
    caller_attachment_type: Mapped[Optional[AttachmentType]] = mapped_column(
        Enum(AttachmentType)
    )
    caller_attachment_bytes: Mapped[Optional[bytes]] = mapped_column(LargeBinary())
    prompt_template: Mapped[Optional[str]] = mapped_column(Text())
    inference_provider_type: Mapped[InferenceProviderType] = mapped_column(
        Enum(InferenceProviderType)
    )
    inference_provider_request_id: Mapped[Optional[str]] = mapped_column(Unicode(50))
    response_chat_text: Mapped[Optional[str]] = mapped_column(Text())
    response_attachment_type: Mapped[Optional[AttachmentType]] = mapped_column(
        Enum(AttachmentType)
    )
    response_attachment_bytes: Mapped[Optional[bytes]] = mapped_column(LargeBinary())

    # time and duration fields
    start_time: Mapped[Optional[datetime]] = mapped_column(DateTime())
    end_time: Mapped[Optional[datetime]] = mapped_column(DateTime())
    inference_duration_seconds: Mapped[Optional[float]] = mapped_column(Float())
    total_duration_seconds: Mapped[Optional[float]] = mapped_column(Float())
    first_created: Mapped[datetime] = mapped_column(DateTime(), default=now_utc)
    last_updated: Mapped[datetime] = mapped_column(
        DateTime(), default=now_utc, onupdate=now_utc
    )

    @classmethod
    def get_exclude_fields_for_logging(cls) -> set[str]:
        exclude_fields = {
            "_sa_instance_state",
            "caller_attachment_bytes",
            "response_attachment_bytes",
        }
        return exclude_fields


class CallerModel(BaseModel):
    """Class for caller model."""

    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)

    # primary and foreign keys
    caller_id: UUID
    chats: List[Chat]

    # core fields
    name: Annotated[str, StringConstraints(max_length=Caller.name.type.length)]
    idp_id: Annotated[str, StringConstraints(max_length=Caller.idp_id.type.length)]

    # time and duration fields
    first_created: datetime
    last_updated: datetime

    @model_validator(mode="after")
    def check_time(self) -> Self:
        _validate_time_fields(self)
        return self


class ChatInputModel(BaseModel):
    """Class for chat input model."""

    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)

    caller_session_id: Annotated[
        str, StringConstraints(max_length=Chat.caller_session_id.type.length)
    ] = Field("<chat session id>")
    caller_chat_text: str = Field("")
    caller_attachment_type: AttachmentType | None
    caller_attachment_bytes: bytes | None = Field("")

    @model_validator(mode="after")
    def check_caller_content(self) -> Self:
        _validate_chat_fields(self)
        return self

    @classmethod
    def get_exclude_fields_for_logging(cls) -> set[str]:
        exclude_fields = "caller_attachment_bytes"
        return exclude_fields


class ChatModel(ChatInputModel):
    """Class for chat model."""

    # primary and foreign keys
    chat_id: UUID
    caller_id: UUID
    caller: Caller

    # core fields
    prompt_template: str
    inference_provider_type: InferenceProviderType
    inference_provider_request_id: Annotated[
        str,
        StringConstraints(max_length=Chat.inference_provider_request_id.type.length),
    ]
    response_chat_text: Annotated[
        str,
        StringConstraints(max_length=Chat.response_chat_text.type.length),
    ]
    response_attachment_type: AttachmentType | None
    response_attachment_bytes: bytes | None

    # time and duration fields
    start_time: Mapped[Optional[datetime]] = mapped_column(DateTime())
    end_time: Mapped[Optional[datetime]] = mapped_column(DateTime())
    inference_duration_seconds: Mapped[Optional[float]] = mapped_column(Float())
    total_duration_seconds: Mapped[Optional[float]] = mapped_column(Float())
    first_created: Mapped[datetime] = mapped_column(DateTime(), default=now_utc)
    last_updated: Mapped[datetime] = mapped_column(
        DateTime(), default=now_utc, onupdate=now_utc
    )

    @model_validator(mode="after")
    def check_caller_content(self) -> Self:
        _validate_chat_fields(self)
        return self

    @model_validator(mode="after")
    def check_time(self) -> Self:
        _validate_time_fields(self)
        _validate_duration_fields(self)
        return self

    @classmethod
    def get_exclude_fields_for_logging(cls) -> set[str]:
        exclude_fields = {
            "caller_attachment_bytes",
            "response_attachment_bytes",
        }
        return exclude_fields


def _validate_chat_fields(self):
    # caller related
    if self.caller_attachment_type is not None:
        assert (
            self.caller_attachment_bytes is not None
            and len(self.caller_attachment_bytes) > 0
        ), "caller attachment bytes is not having data"

    # response related
    if (
        hasattr(self, "response_attachment_type")
        and hasattr(self, "response_attachment_bytes")
        and self.response_attachment_type is not None
    ):
        assert (
            self.response_attachment_bytes is not None
            and len(self.response_attachment_bytes) > 0
        ), "response attachment bytes is not having data"


def _validate_time_fields(self):
    if self.last_updated and self.first_created:
        assert self.last_updated.replace(tzinfo=None) >= self.first_created.replace(
            tzinfo=None
        ), f"last updated - {self.last_updated} is less than first created - {self.first_created}"


def _validate_duration_fields(self):
    if self.end_time and self.start_time:
        assert self.end_time.replace(tzinfo=None) > self.start_time.replace(
            tzinfo=None
        ), f"end time - {self.end_time} is less than start time = {self.start_time}"
    if (
        self.total_duration_seconds
        and hasattr(self, "inference_duration_seconds")
        and self.inference_duration_seconds
    ):
        assert (
            self.total_duration_seconds >= self.inference_duration_seconds
        ), f"total duration seconds = {self.total_duration_seconds} is less than inference duration seconds - {self.inference_duration_seconds}"
