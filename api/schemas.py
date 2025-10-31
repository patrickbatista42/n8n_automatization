from pydantic import BaseModel, EmailStr, ConfigDict
from datetime import datetime
from .models import AppointmentStatus
from typing import List, Optional

class ConfigBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

class PatientBase(BaseModel):
    name: str
    email: EmailStr
    phone: Optional[str] = None

class PatientCreate(PatientBase):
    pass

class Patient(PatientBase, ConfigBase):
    id: int

class DoctorBase(BaseModel):
    name: str
    specialty: str

class Doctor(DoctorBase, ConfigBase):
    id: int

class SlotBase(BaseModel):
    start_time: datetime
    end_time: datetime
    is_booked: bool

class Slot (SlotBase, ConfigBase):
    id: int
    doctor_id: int
    doctor: Doctor

class AppointmentBase(BaseModel):
    pass

class AppointmentCreate(AppointmentBase):
    slot_id: int
    patient_id: int

class Appointment (AppointmentBase, ConfigBase):
    id: int
    created_at: datetime
    status: AppointmentStatus
    slot: Slot
    patient: Patient

class PaymentInfo(BaseModel):
    methods: List[str]
    value: str
    pix_key: Optional[str] = None
