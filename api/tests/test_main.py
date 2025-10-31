import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from .test_database import TestingSessionLocal, engine, override_get_db
from api.main import app, get_db
from api.models import Base, Doctor, Slot, Patient, AppointmentStatus
from api.seed import seed_database 


@pytest.fixture(scope="function")
def db_session():
    Base.metadata.create_all(bind=engine)
    
    db = TestingSessionLocal()
    
    try:
        dr_test = Doctor(name="Dr. Teste", specialty="Testologia")
        pac_test = Patient(name="Paciente Teste", email="teste@teste.com")
        db.add_all([dr_test, pac_test])
        db.commit()

        slot_disponivel = Slot(
            doctor_id=dr_test.id,
            start_time=datetime.utcnow() + timedelta(days=1, hours=1),
            end_time=datetime.utcnow() + timedelta(days=1, hours=2),
            is_booked=False
        )
        slot_ocupado = Slot(
            doctor_id=dr_test.id,
            start_time=datetime.utcnow() + timedelta(days=1, hours=2),
            end_time=datetime.utcnow() + timedelta(days=1, hours=3),
            is_booked=True
        )
        slot_passado = Slot(
            doctor_id=dr_test.id,
            start_time=datetime.utcnow() - timedelta(days=1),
            end_time=datetime.utcnow() - timedelta(days=1, hours=1),
            is_booked=False
        )
        
        db.add_all([slot_disponivel, slot_ocupado, slot_passado])
        db.commit()
        
        yield db
    
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client(db_session):
    app.dependency_overrides[get_db] = lambda: db_session
    
    with TestClient(app) as c:
        yield c
    
    app.dependency_overrides = {}

def test_health_check(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"status": "API online"}

def test_get_payment_info(client):
    response = client.get("/pagamento/")
    assert response.status_code == 200
    assert response.json()["value"] == "O valor da consulta padrão é R$200,00."

def test_get_available_slots(client, db_session: Session):
    response = client.get("/horarios/")
    assert response.status_code == 200
    
    data = response.json()
    assert len(data) == 1
    assert data[0]["is_booked"] == False
    assert data[0]["doctor"]["name"] == "Dr. Teste"

def test_create_appointment_success(client, db_session: Session):
    
    paciente = db_session.query(Patient).first()
    slot = db_session.query(Slot).filter(Slot.is_booked == False, Slot.start_time > datetime.utcnow()).first()
    
    response = client.post(
        "/agendar/",
        json={"slot_id": slot.id, "patient_id": paciente.id}
    )
    if response.status_code != 201:
        print(f"\n[DEBUG] ERRO 500 EM create_success: {response.json()}\n")

    assert response.status_code == 201
    data = response.json()
    assert data["status"] == AppointmentStatus.CONFIRMED.value
    assert data["patient"]["id"] == paciente.id
    assert data["slot"]["id"] == slot.id
    
    slot_no_db = db_session.get(Slot, slot.id)
    assert slot_no_db.is_booked == True

def test_create_appointment_booked_slot(client, db_session: Session):
    paciente = db_session.query(Patient).first()
    slot_ocupado = db_session.query(Slot).filter(Slot.is_booked == True).first()

    response = client.post(
        "/agendar/",
        json={"slot_id": slot_ocupado.id, "patient_id": paciente.id}
    )
    
    assert response.status_code == 400
    assert "Este horário já foi agendado" in response.json()["detail"]

def test_cancel_appointment(client, db_session: Session):
    
    paciente = db_session.query(Patient).first()
    slot = db_session.query(Slot).filter(Slot.is_booked == False).first()
    
    response_agenda = client.post(
        "/agendar/",
        json={"slot_id": slot.id, "patient_id": paciente.id}
    )

    if response_agenda.status_code != 201:
        print(f"\n[DEBUG] ERRO 500 EM cancel_appointment (setup): {response_agenda.json()}\n")

    assert response_agenda.status_code == 201
    appointment_id = response_agenda.json()["id"]
    
    response_cancela = client.post(f"/cancelar/{appointment_id}")
    
    assert response_cancela.status_code == 200
    assert response_cancela.json()["status"] == AppointmentStatus.CANCELLED.value
    
    slot_no_db = db_session.get(Slot, slot.id)
    assert slot_no_db.is_booked == False