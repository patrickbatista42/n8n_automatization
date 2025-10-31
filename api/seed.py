# api/seed.py
from datetime import datetime, timedelta
import random

# Importações de Banco de Dados e Modelos
from .database import SessionLocal, create_db_and_tables, engine
from .models import Base, Doctor, Patient, Slot, Appointment, AppointmentStatus

def create_fake_appointment(db: Session, doctor: Doctor, patient: Patient, start_time: datetime, status: AppointmentStatus, created_days_ago: int):
    """
    Função auxiliar para criar um Slot E um Agendamento
    de forma consistente.
    """
    
    # 1. Cria o Slot (que estará ocupado)
    db_slot = Slot(
        doctor_id=doctor.id,
        start_time=start_time,
        end_time=start_time + timedelta(hours=1),
        is_booked=True # O slot já nasce ocupado
    )
    
    # 2. Cria o Agendamento
    db_appointment = Appointment(
        slot=db_slot,  # Linka o objeto Slot
        patient=patient, # Linka o objeto Patient
        created_at=datetime.utcnow() - timedelta(days=created_days_ago), # Simula quando foi criado
        status=status
    )
    
    db.add(db_slot)
    db.add(db_appointment)
    return db_appointment

def seed_database():
    """
    Popula o banco de dados com dados fictícios ricos
    para visualizações e testes.
    """
    
    # --- 1. Resetar o Banco ---
    # Limpa todas as tabelas e as recria
    Base.metadata.drop_all(bind=engine)
    create_db_and_tables()
    
    db = SessionLocal()
    
    try:
        # --- 2. Criar Entidades Principais ---
        print("Criando Médicos e Pacientes...")
        
        # Médicos
        dr_silva = Doctor(name="Dr. João Silva", specialty="Clínico Geral")
        dra_mendes = Doctor(name="Dra. Ana Mendes", specialty="Cardiologista")
        dr_costa = Doctor(name="Dr. Carlos Costa", specialty="Dermatologista")
        dra_lima = Doctor(name="Dra. Beatriz Lima", specialty="Ortopedista")
        db.add_all([dr_silva, dra_mendes, dr_costa, dra_lima])
        
        # Pacientes
        p_carlos = Patient(name="Carlos Pereira", email="carlos.p@exemplo.com", phone="47999887766")
        p_maria = Patient(name="Maria Souza", email="maria.souza@exemplo.com", phone="47988776655")
        p_joao = Patient(name="João Alves", email="joao.a@exemplo.com", phone="47977665544")
        p_lucia = Patient(name="Lúcia Ferreira", email="lucia.f@exemplo.com", phone="47966554433")
        p_rafael = Patient(name="Rafael Oliveira", email="rafael.o@exemplo.com", phone="47955443322")
        db.add_all([p_carlos, p_maria, p_joao, p_lucia, p_rafael])
        
        db.commit() # Commit para obter os IDs

        # Pega as listas com IDs
        doctors = db.query(Doctor).all()
        patients = db.query(Patient).all()

        # --- 3. Criar Agendamentos Históricos (Para Gráficos) ---
        print("Criando histórico de agendamentos (passados)...")
        
        # Para Viz 2 (Volume) e Viz 3 (Status)
        for i in range(100): # Criar 100 agendamentos históricos
            # Escolhe dia (últimos 90 dias) e hora (horário comercial)
            day_offset = random.randint(1, 90)
            hour_offset = random.randint(9, 17)
            
            # Seta o status (80% Confirmado, 20% Cancelado)
            status = AppointmentStatus.CONFIRMED if random.random() < 0.8 else AppointmentStatus.CANCELLED
            
            # Escolhe médico e paciente aleatórios
            rand_doctor = random.choice(doctors)
            rand_patient = random.choice(patients)
            
            # Define a data/hora do agendamento (no passado)
            start_time = datetime.utcnow().replace(hour=hour_offset, minute=0) - timedelta(days=day_offset)
            
            # Define quando foi criado (entre o dia do agendamento e 7 dias antes)
            created_offset = day_offset + random.randint(0, 7)
            
            create_fake_appointment(db, rand_doctor, rand_patient, start_time, status, created_offset)

        # --- 4. Criar Agendamentos Futuros (Para Viz 4) ---
        print("Criando agendamentos futuros (confirmados)...")
        
        # Para Viz 4 (Próximas Consultas)
        create_fake_appointment(db, dra_mendes, p_carlos, datetime.utcnow().replace(hour=10, minute=0) + timedelta(days=2), AppointmentStatus.CONFIRMED, 1)
        create_fake_appointment(db, dr_silva, p_maria, datetime.utcnow().replace(hour=11, minute=0) + timedelta(days=3), AppointmentStatus.CONFIRMED, 2)
        create_fake_appointment(db, dr_costa, p_joao, datetime.utcnow().replace(hour=14, minute=0) + timedelta(days=3), AppointmentStatus.CONFIRMED, 1)

        # --- 5. Criar Slots Futuros (Para N8N) ---
        print("Criando slots futuros (disponíveis)...")
        
        # Para o N8N poder agendar
        available_slots = []
        base_time = datetime.utcnow().replace(minute=0, second=0, microsecond=0) + timedelta(days=1)
        
        for day in range(1, 5): # Próximos 4 dias
            for hour in range(9, 17): # Horário comercial
                # Chance de 50% de ter um slot disponível
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