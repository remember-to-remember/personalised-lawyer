""" Module for inserting caller data into the database. """

from datetime import UTC, datetime
from uuid import UUID

from api.entities import Caller
from sqlalchemy import create_engine
from sqlalchemy.orm import Session


def insert_callers(connection_string: str, debug_mode: bool) -> None:
    """Insert caller data into the database."""

    callers = [
        {
            "caller_id": UUID("00000000-0000-0000-0000-000000000001"),
            "name": "Ankur Soni",
            "idp_id": "google-oauth2|103311653287323190363",
            "email": "soniankur@gmail.com",
            "first_created": datetime.now(UTC),
            "last_updated": datetime.now(UTC),
        }
    ]

    engine = create_engine(connection_string, echo=debug_mode)
    with Session(engine) as session:
        for caller in callers:
            if (
                session.query(Caller)
                .filter_by(caller_id=caller["caller_id"])
                .one_or_none()
            ):
                continue
            session.add(Caller(**caller))
        session.commit()
