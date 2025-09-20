from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime

# Crear la base de datos SQLite
SQLALCHEMY_DATABASE_URL = "sqlite:///./activities.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})

# Crear la sesión
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Crear la base para los modelos
Base = declarative_base()

class Activity(Base):
    __tablename__ = "activities"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String)
    schedule = Column(String)
    max_capacity = Column(Integer)
    category = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    status = Column(String, default="active")
    
    participants = relationship("Participant", back_populates="activity")

class Participant(Base):
    __tablename__ = "participants"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, index=True)
    activity_id = Column(Integer, ForeignKey("activities.id"))
    registered_at = Column(DateTime, default=datetime.utcnow)
    status = Column(String, default="active")
    
    activity = relationship("Activity", back_populates="participants")

# Crear todas las tablas
Base.metadata.create_all(bind=engine)

# Función de utilidad para obtener la sesión de la base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()