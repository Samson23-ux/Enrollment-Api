from datetime import datetime, timezone
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey, UUID, Column, DateTime, PrimaryKeyConstraint

from app.database.base import Base


class Enrollment(Base):
    __tablename__ = "enrollments"

    user_id = Column(
        UUID, ForeignKey("users.id", name="enrol_user_id_fk", ondelete="CASCADE")
    )
    course_id = Column(
        UUID, ForeignKey("courses.id", name="enrol_course_id_fk", ondelete="CASCADE")
    )
    created_at = Column(
        DateTime(timezone=True), default=datetime.now(tz=timezone.utc), nullable=False
    )

    __table_args__ = (PrimaryKeyConstraint("user_id", "course_id", name="enrol_pk"),)

    user = relationship("User", back_populates="enrollments", viewonly=True)
    course =  relationship("Course", back_populates="enrollments", viewonly=True)
