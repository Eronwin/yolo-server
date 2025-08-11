from datetime import datetime
from typing import Optional

import sqlalchemy
from pydantic import Field

from backend.schemas.common import UTCDateTime


class TimestampsMixin:
    # Mixin that define timestamp column.

    __abstract__ = True
    __config__ = None

    __created_at_name__ = "created_at"
    __updated_at_name__ = "updated_at"
    __deleted_at_name__ = "deleted_at"
    __datetime_func__ = sqlalchemy.func.now()

    created_at = sqlalchemy.Column(
        __created_at_name__,
        UTCDateTime,
        default=__datetime_func__,
        nullable=False,
    )

    updated_at = sqlalchemy.Column(
        __updated_at_name__,
        UTCDateTime,
        default=__datetime_func__,
        onupdate=__datetime_func__,
        nullable=False,
    )

    deleted_at: Optional[datetime] = Field(
        sa_column=sqlalchemy.Column(UTCDateTime), default=None
    )
