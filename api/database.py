from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import DATABASE_URL, Base 
import redis
import json

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_db_and_tables():
    Base.metadata.create_all(bind=engine)

try:
    redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
    redis_client.ping()
    print("Conectado ao Redis com sucesso!")
except redis.exceptions.ConnectionError as e:
    print(f"Aviso: Não foi possível conectar ao Redis. O cache está desabilitado. Erro: {e}")
    redis_client = None