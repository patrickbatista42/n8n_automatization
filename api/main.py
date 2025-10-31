from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from . import crud, models, schemas
from .database import get_db, create_db_and_tables
from pydantic import EmailStr

create_db_and_tables()

app = FastAPI(
    title="API de Atendimento Médico",
    description="API para agendamento médico",
    version="1.0.0"
)

# Endpoints

@app.get("/", tags=["Status"])
def read_root():
         return {"status": "API online"}

@app.get("/horarios", response_model=List[schemas.Slot], tags=["Agendamentos"])
def get_available_slots(db: Session = Depends(get_db)):
        slots = crud.get_available_slots(db)
        return slots

@app.post("/agendar", response_model=schemas.Appointment, status_code=201, tags=["Agendamentos"])
def create_appointment(appointment: schemas.AppointmentCreate, db: Session = Depends(get_db)):
    try:
        appointment_id = crud.create_appointment(db, appointment=appointment)
        db_appointment = crud.get_appointment(db, appointment_id=appointment_id)
        return db_appointment
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        error_type = type(e).__name__
        raise HTTPException(status_code=500, detail=f"ERRO REAL: {error_type} - {str(e)}")
        
@app.post("/cancelar/{appointment_id}", response_model=schemas.Appointment, tags=["Agendamentos"])
def cancel_appointment(appointment_id: int, db: Session = Depends(get_db)):
    try:
        cancelled_id = crud.cancel_appointment(db, appointment_id=appointment_id)
        db_appointment = crud.get_appointment(db, appointment_id=cancelled_id)
        return db_appointment
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) 
    except Exception as e:
        error_type = type(e).__name__
        raise HTTPException(status_code=500, detail=f"ERRO REAL: {error_type} - {str(e)}")

@app.get("/pagamento", response_model=schemas.PaymentInfo, tags=["Informações"])
def get_payment_info():
        return schemas.PaymentInfo(
                methods=["Pix", "Cartão de Crédito", "Convênio"],
                value="O valor da consulta padrão é R$200,00.",
                pix_key="doutor@agendamento.com"
        )

@app.post("/pacientes/", response_model=schemas.Patient, status_code=201, tags=["Pacientes"])
def create_or_get_patient(patient: schemas.PatientCreate, db: Session = Depends(get_db)):
        db_patient = crud.get_patient_by_email(db, email=patient.email)
        if db_patient:
                return db_patient
        
        db_patient = crud.create_patient(db, patient=patient)
        if db_patient is None:
                raise HTTPException(status_code=400, detail= "Email já cadastrado.")
        return db_patient

@app.get("/pacientes/meus-agendamentos/", response_model=List[schemas.Appointment], tags=["Pacientes"])
def get_my_appointments(email: EmailStr = Query(..., description="Email do paciente para buscar agendamentos."), 
                        db: Session = Depends(get_db)):
    try:
        appointments = crud.get_patient_active_appointments(db, email=email)
        return appointments
    except Exception as e:
        error_type = type(e).__name__
        raise HTTPException(status_code=500, detail=f"ERRO REAL: {error_type} - {str(e)}")