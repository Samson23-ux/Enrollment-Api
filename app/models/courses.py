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
    CheckConstraint,
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
    capacity = Column(
        Integer,
        CheckConstraint("capacity >= 10", name="courses_capacity_ck"),
        nullable=False,
    )
    duration = Column(Integer, nullable=False)
    # when a user is deleted, the course is assigned to another instructor
    instructor_id = Column(
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

    instructor = relationship(
        "User", foreign_keys="Course.instructor_id", viewonly=True
    )

    users = relationship(
        "User", back_populates="courses", secondary="enrollments", viewonly=True
    )
    enrollments = relationship("Enrollment", back_populates="course", viewonly=True)
