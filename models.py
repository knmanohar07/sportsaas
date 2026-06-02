from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
import datetime
from database import Base

class Player(Base):
    __tablename__ = "players"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    age = Column(Integer, nullable=False)
    emergency_contact = Column(String, nullable=False)
    medical_info = Column(String, nullable=True)
    joined_date = Column(DateTime, default=datetime.datetime.utcnow)

    # Links player to their attendance and payments
    attendance_records = relationship("Attendance", back_populates="player")
    payments = relationship("Payment", back_populates="player")


class Session(Base):
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True, index=True)
    turf_name = Column(String, index=True, nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    capacity = Column(Integer, default=20)

    attendance_records = relationship("Attendance", back_populates="session")


class Attendance(Base):
    __tablename__ = "attendance"

    id = Column(Integer, primary_key=True, index=True)
    player_id = Column(Integer, ForeignKey("players.id"), nullable=False)
    session_id = Column(Integer, ForeignKey("sessions.id"), nullable=False)
    attended = Column(Boolean, default=False)
    scanned_at = Column(DateTime, default=datetime.datetime.utcnow)

    player = relationship("Player", back_populates="attendance_records")
    session = relationship("Session", back_populates="attendance_records")


class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    player_id = Column(Integer, ForeignKey("players.id"), nullable=False)
    amount_due = Column(Float, nullable=False)
    amount_paid = Column(Float, default=0.0)
    due_date = Column(DateTime, nullable=False)
    status = Column(String, default="Pending")

    player = relationship("Player", back_populates="payments")