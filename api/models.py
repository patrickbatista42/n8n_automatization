import enum
from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.orm import declarative_base
from datetime import datetime
from datetime import UTC

# Define a URL do banco de dados SQLite
DATABASE_URL = "sqlite:///./med_agenda.db"
Base = declarative_base()

# Enum para status de agendamento
class AppointmentStatus(enum.Enum):
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    PENDING = "pending"

class Doctor(Base):
    """Modelo para um Médico."""
    __tablename__ = "doctors"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    specialty = Column(String)
    
    # Relacionamento: Um médico pode ter vários horários disponíveis
    slots = relationship("Slot", back_populates="doctor")

class Patient(Base):
    """Modelo para um Paciente."""
    __tablename__ = "patients"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    email = Column(String, unique=True, index=True)
    phone = Column(String)
    
    # Relacionamento: Um paciente pode ter vários agendamentos
    appointments = relationship("Appointment", back_populates="patient")

class Slot(Base):
    """Modelo para um Horário Disponível na agenda."""
    __tablename__ = "slots"
    
    id = Column(Integer, primary_key=True, index=True)
    doctor_id = Column(Integer, ForeignKey("doctors.id"))
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    is_booked = Column(Boolean, default=False)
    
    # Relacionamentos
    doctor = relationship("Doctor", back_populates="slots")
    appointment = relationship("Appointment", back_populates="slot", uselist=False) # Um slot só pode ter um agendamento

class Appointment(Base):
    """Modelo para um Agendamento."""
    __tablename__ = "appointments"
    
    id = Column(Integer, primary_key=True, index=True)
    slot_id = Column(Integer, ForeignKey("slots.id"), unique=True) # Um agendamento por slot
    patient_id = Column(Integer, ForeignKey("patients.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    status = Column(Enum(AppointmentStatus), default=AppointmentStatus.PENDING)
    
    # Relacionamentos
    slot = relationship("Slot", back_populates="appointment")
    patient = relationship("Patient", back_populates="appointments")