from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base
import enum
from typing import Optional


class TeachingModeEnum(str, enum.Enum):
    online = "online"
    in_person = "in_person"
    hybrid = "hybrid"


class Student(Base):
    __tablename__ = "students"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    city = Column(String, nullable=True)
    address = Column(String, nullable=True)
    preferred_subjects = Column(String, nullable=True)  # comma-separated subject names or ids
    max_hourly_rate = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class Tutor(Base):
    __tablename__ = "tutors"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    phone = Column(String, nullable=True)
    city = Column(String, nullable=True)
    address = Column(String, nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    hourly_rate = Column(Float, nullable=False, default=0.0)
    teaching_mode = Column(Enum(TeachingModeEnum), default=TeachingModeEnum.online)
    bio = Column(Text, nullable=True)
    overall_rating = Column(Float, default=0.0)
    number_of_reviews = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    subjects = relationship("Subject", secondary="tutor_subjects", back_populates="tutors")
    reviews = relationship("Review", back_populates="tutor")


class Subject(Base):
    __tablename__ = "subjects"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
    tutors = relationship("Tutor", secondary="tutor_subjects", back_populates="subjects")


class TutorSubject(Base):
    __tablename__ = "tutor_subjects"
    id = Column(Integer, primary_key=True, index=True)
    tutor_id = Column(Integer, ForeignKey("tutors.id"))
    subject_id = Column(Integer, ForeignKey("subjects.id"))


class Review(Base):
    __tablename__ = "reviews"
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    tutor_id = Column(Integer, ForeignKey("tutors.id"), nullable=False)
    rating = Column(Integer, nullable=False)
    comment = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    tutor = relationship("Tutor", back_populates="reviews")


class LessonRequest(Base):
    __tablename__ = "lesson_requests"
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    tutor_id = Column(Integer, ForeignKey("tutors.id"), nullable=False)
    subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=False)
    status = Column(String, default="pending")
    requested_date = Column(DateTime, nullable=True)
    notes = Column(Text, nullable=True)
