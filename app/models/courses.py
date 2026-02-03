from datetime import datetime, timezone
from sqlalchemy.orm import relationship
from sqlalchemy import (
    text,
    UUID,
    Index,
    Column,
    Boolean,
    VARCHAR,
    Integer,
    DateTime,
    ForeignKey,
    UniqueConstraint,
    PrimaryKeyConstraint,
)


from app.database.base import Base


class Course(Base):
    __tablename__ = "courses"

    id = Column(UUID, default=text("uuid_generate_v4()"))
    title = Column(VARCHAR(20), nullable=False)
    description = Column(VARCHAR(50), nullable=False)
    code = Column(VARCHAR(20), nullable=False)
    capacity = Column(Integer, nullable=False)
    duration = Column(Integer, nullable=False)
    # when a user is deleted, the course is assigned to another instructor
    instructor = Column(
        UUID,
        ForeignKey("users.id", name="courses_instructor_fk", ondelete="RESTRICT"),
        nullable=False,
    )
    total_students = Column(
        Integer, nullable=False
    )  # total students currently enrolled for the course
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.now(timezone.utc))

    __table_args__ = (
        Index(
            "idx_courses_title",
            title,
            postgresql_using="gin",
            postgresql_ops={"title": "gin_trgm_ops"},
        ),
        PrimaryKeyConstraint("id", name="courses_id_pk"),
        UniqueConstraint("code", name="courses_code_unique_key"),
    )

    users = relationship(
        "User", back_populates="courses", secondary="Enrollment", viewonly=True
    )
    enrollments = relationship("Enrollment", back_populates="course", viewonly=True)
