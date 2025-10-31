
from datetime import datetime, timedelta
import random
from .database import SessionLocal, create_db_and_tables, engine
from .models import Base, Doctor, Patient, Slot, Appointment, AppointmentStatus
from sqlalchemy.orm import Session

def create_fake_appointment(db: Session, doctor: Doctor, patient: Patient, start_time: datetime, status: AppointmentStatus, created_days_ago: int):
    db_slot = Slot(
        doctor_id=doctor.id,
        start_time=start_time,
        end_time=start_time + timedelta(hours=1),
        is_booked=True 
    )

    db_appointment = Appointment(
        slot=db_slot,  
        patient=patient, 
        created_at=datetime.utcnow() - timedelta(days=created_days_ago),
        status=status
    )
    
    db.add(db_slot)
    db.add(db_appointment)
    return db_appointment

def seed_database():
    Base.metadata.drop_all(bind=engine)
    create_db_and_tables()
    
    db = SessionLocal()
    
    try:
        print("Criando Médicos e Pacientes...")
        dr_silva = Doctor(name="Dr. João Silva", specialty="Clínico Geral")
        dra_mendes = Doctor(name="Dra. Ana Mendes", specialty="Cardiologista")
        dr_costa = Doctor(name="Dr. Carlos Costa", specialty="Dermatologista")
        dra_lima = Doctor(name="Dra. Beatriz Lima", specialty="Ortopedista")
        db.add_all([dr_silva, dra_mendes, dr_costa, dra_lima])
        p_carlos = Patient(name="Carlos Pereira", email="carlos.p@exemplo.com", phone="47999887766")
        p_maria = Patient(name="Maria Souza", email="maria.souza@exemplo.com", phone="47988776655")
        p_joao = Patient(name="João Alves", email="joao.a@exemplo.com", phone="47977665544")
        p_lucia = Patient(name="Lúcia Ferreira", email="lucia.f@exemplo.com", phone="47966554433")
        p_rafael = Patient(name="Rafael Oliveira", email="rafael.o@exemplo.com", phone="47955443322")
        db.add_all([p_carlos, p_maria, p_joao, p_lucia, p_rafael])
        
        db.commit()
        doctors = db.query(Doctor).all()
        patients = db.query(Patient).all()
        print("Criando histórico de agendamentos (passados)...")
        for i in range(100): 
            day_offset = random.randint(1, 90)
            hour_offset = random.randint(9, 17)
            status = AppointmentStatus.CONFIRMED if random.random() < 0.8 else AppointmentStatus.CANCELLED
            rand_doctor = random.choice(doctors)
            rand_patient = random.choice(patients)
            start_time = datetime.utcnow().replace(hour=hour_offset, minute=0) - timedelta(days=day_offset)
            created_offset = day_offset + random.randint(0, 7)
            
            create_fake_appointment(db, rand_doctor, rand_patient, start_time, status, created_offset)
        print("Criando agendamentos futuros (confirmados)...")
        create_fake_appointment(db, dra_mendes, p_carlos, datetime.utcnow().replace(hour=10, minute=0) + timedelta(days=2), AppointmentStatus.CONFIRMED, 1)
        create_fake_appointment(db, dr_silva, p_maria, datetime.utcnow().replace(hour=11, minute=0) + timedelta(days=3), AppointmentStatus.CONFIRMED, 2)
        create_fake_appointment(db, dr_costa, p_joao, datetime.utcnow().replace(hour=14, minute=0) + timedelta(days=3), AppointmentStatus.CONFIRMED, 1)

        print("Criando slots futuros (disponíveis)...")

        available_slots = []
        base_time = datetime.utcnow().replace(minute=0, second=0, microsecond=0) + timedelta(days=1)
        
        for day in range(1, 5): 
            for hour in range(9, 17): 
                if random.random() < 0.5:
                    available_slots.append(Slot(
                        doctor=random.choice(doctors),
                        start_time=base_time.replace(hour=hour) + timedelta(days=day),
                        end_time=base_time.replace(hour=hour+1) + timedelta(days=day),
                        is_booked=False
                    ))
        
        db.add_all(available_slots)
        
        db.commit()
        
        print("\nBanco de dados populado com sucesso com dados ricos!")

    except Exception as e:
        print(f"Erro ao popular o banco: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("Iniciando o processo de seeding do banco de dados...")
    seed_database()