from datetime import datetime, timezone
from sqlalchemy.orm import relationship
from sqlalchemy import (
    Enum,
    text,
    UUID,
    Text,
    Index,
    Column,
    Boolean,
    VARCHAR,
    DateTime,
    ForeignKey,
    UniqueConstraint,
    PrimaryKeyConstraint,
)


from app.database.base import Base
from app.api.v1.schemas.users import UserRole


class User(Base):
    __tablename__ = "users"

    id = Column(UUID, default=text("uuid_generate_v4()"))
    name = Column(VARCHAR(20), nullable=False)
    email = Column(VARCHAR(20), nullable=False)
    nationality = Column(VARCHAR(25), nullable=False)
    hashed_password = Column(Text, nullable=False)
    role_id = Column(
        UUID,
        ForeignKey("roles.id", name="users_role_id_fk", ondelete="RESTRICT"),
        nullable=False,
    )
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(
        DateTime(timezone=True), default=datetime.now(tz=timezone.utc), nullable=False
    )
    delete_at = Column(DateTime(timezone=True))

    __table_args__ = (
        Index("idx_users_email", email),
        Index("idx_users_role_id", role_id),
        Index(
            "idx_users_name",
            name,
            postgresql_using="gin",
            postgresql_ops={"name": "gin_trgm_ops"},
        ),
        PrimaryKeyConstraint("id", name="users_id_pk"),
        UniqueConstraint("email", name="users_email_unique_key"),
    )

    role = relationship("Role", viewonly=True)
    courses = relationship(
        "Course", back_populates="users", secondary="enrollments", passive_deletes=True
    )
    enrollments = relationship("Enrollment", back_populates="user", viewonly=True)


class Role(Base):
    __tablename__ = "roles"

    id = Column(UUID, default=text("uuid_generate_v4()"))
    name = Column(Enum(UserRole), nullable=False)

    __table_args__ = (
        PrimaryKeyConstraint("id", name="roles_id_pk"),
        UniqueConstraint("name", name="roles_name_unique_key"),
    )
