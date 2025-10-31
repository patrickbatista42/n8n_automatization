from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import IntegrityError
from datetime import datetime
import json
from . import models, schemas
from .database import redis_client

CACHE_KEY_AVAILABLE_SLOTS = "available_slots"
CACHE_EXPIRATION_SECONDS = 300

def get_available_slots(db: Session, skip: int = 0, limit: int = 100):
    
    if redis_client:
        try:
            cached_data = redis_client.get(CACHE_KEY_AVAILABLE_SLOTS)
            if cached_data:
                print("CACHE HIT: Retornando dados do Redis.")
                return json.loads(cached_data) 
        except Exception as e:
            print(f"Erro ao ler do cache Redis: {e}")
    print("CACHE MISS: Buscando dados do SQLite.")
    now = datetime.utcnow()
    db_slots = db.query(models.Slot)\
                 .options(joinedload(models.Slot.doctor))\
                 .filter(models.Slot.is_booked == False)\
                 .filter(models.Slot.start_time > now)\
                 .order_by(models.Slot.start_time)\
                 .offset(skip)\
                 .limit(limit)\
                 .all()
    pydantic_slots = [schemas.Slot.model_validate(slot) for slot in db_slots]
    json_data_to_cache = json.dumps([slot.model_dump() for slot in pydantic_slots], default=str)

    if redis_client:
        try:
            redis_client.setex(
                CACHE_KEY_AVAILABLE_SLOTS,
                CACHE_EXPIRATION_SECONDS,
                json_data_to_cache
            )
            print("CACHE SET: Dados salvos no Redis.")
        except Exception as e:
            print(f"Erro ao salvar no cache Redis: {e}")
    return pydantic_slots

def _invalidate_slots_cache():
    if redis_client:
        try:
            print("CACHE INVALIDATION: Deletando a chave 'available_slots'.")
            redis_client.delete(CACHE_KEY_AVAILABLE_SLOTS)
        except Exception as e:
            print(f"Erro ao invalidar o cache: {e}")

def get_patient(db: Session, patient_id: int):
    return db.query(models.Patient).filter(models.Patient.id == patient_id).first()

def get_patient_by_email(db: Session, email: str):
    return db.query(models.Patient).filter(models.Patient.email == email).first()

def create_patient(db: Session, patient: schemas.PatientCreate):
    db_patient = models.Patient(**patient.model_dump())
    try:
        db.add(db_patient)
        db.commit()
        db.refresh(db_patient)
        return db_patient
    except IntegrityError:
        db.rollback()
        return None
    
def get_available_slots(db: Session, skip: int = 0, limit: int = 100):
    now = datetime.utcnow()
    if redis_client:
        try:
            cached_data = redis_client.get(CACHE_KEY_AVAILABLE_SLOTS)
            if cached_data:
                print("CACHE HIT: Retornando dados do Redis.")
                return json.loads(cached_data) 
        except Exception as e:
            print(f"Erro ao ler do cache Redis: {e}")
    print("CACHE MISS: Buscando dados do SQLite.")
    now = datetime.utcnow()
    db_slots = db.query(models.Slot)\
                 .options(joinedload(models.Slot.doctor))\
                 .filter(models.Slot.is_booked == False)\
                 .filter(models.Slot.start_time > now)\
                 .order_by(models.Slot.start_time)\
                 .offset(skip)\
                 .limit(limit)\
                 .all()
    pydantic_slots = [schemas.Slot.model_validate(slot) for slot in db_slots]
    pydantic_dicts = [slot.model_dump() for slot in pydantic_slots] 
    json_data_to_cache = json.dumps(pydantic_dicts, default=str)
    if redis_client:
        try:
            redis_client.setex(
                CACHE_KEY_AVAILABLE_SLOTS,
                CACHE_EXPIRATION_SECONDS,
                json_data_to_cache
            )
            print("CACHE SET: Dados salvos no Redis.")
        except Exception as e:
            print(f"Erro ao salvar no cache Redis: {e}")

    return pydantic_dicts

def get_appointment(db: Session, appointment_id: int):
    db_appointment = db.query(models.Appointment)\
        .options(
            joinedload(models.Appointment.slot).joinedload(models.Slot.doctor),
            joinedload(models.Appointment.patient)
        )\
        .filter(models.Appointment.id == appointment_id)\
        .first()
    return db_appointment

def create_appointment(db: Session, appointment: schemas.AppointmentCreate) -> int:

    db_slot = db.query(models.Slot)\
        .options(joinedload(models.Slot.doctor))\
        .filter(models.Slot.id == appointment.slot_id)\
        .first()

    db_patient = db.query(models.Patient).filter(models.Patient.id == appointment.patient_id).first()
    if not db_patient:
        raise ValueError("Paciente não encontrado.")

    if not db_slot:
        raise ValueError("Horário (Slot) não encontrado")
    if db_slot.is_booked:
        raise ValueError("Este horário já foi agendado")
    if db_slot.start_time <= datetime.utcnow():
        raise ValueError("Não é possível agendar um horário no passado.")

    db_slot.is_booked = True
    db_appointment = models.Appointment(
        slot = db_slot,
        patient = db_patient,
        status = models.AppointmentStatus.CONFIRMED
    ) 

    try:
        db.add(db_appointment)
        db.commit()
        db.refresh(db_appointment)
        _invalidate_slots_cache()
        return db_appointment.id
    except Exception as e:
        db.rollback()
        raise e
    
def cancel_appointment(db: Session, appointment_id: int) -> int: # Alterado: Retorna int
    
    db_appointment = get_appointment(db, appointment_id=appointment_id)

    if not db_appointment:
        raise ValueError("Agendamento não encontrado")
    if db_appointment.status == models.AppointmentStatus.CANCELLED:
        raise ValueError("Agendamento já está cancelado.")
    
    db_appointment.slot.is_booked = False
    db_appointment.status = models.AppointmentStatus.CANCELLED

    try:
        db.commit()
        _invalidate_slots_cache()
        return db_appointment.id
    except Exception as e:
        db.rollback()
        raise e
    
def get_patient_active_appointments(db: Session, email: str):
    db_patient = get_patient_by_email(db, email=email)
    
    if not db_patient:
        return []
    
    now = datetime.utcnow()
    
    return db.query(models.Appointment)\
        .join(models.Slot)\
        .filter(models.Appointment.patient_id == db_patient.id)\
        .filter(models.Appointment.status != models.AppointmentStatus.CANCELLED)\
        .filter(models.Slot.start_time >= now)\
        .options(
            joinedload(models.Appointment.slot).joinedload(models.Slot.doctor),
            joinedload(models.Appointment.patient)
        )\
        .order_by(models.Slot.start_time)\
        .all()