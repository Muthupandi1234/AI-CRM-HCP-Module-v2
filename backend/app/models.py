from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

DATABASE_URL = "sqlite:///./hcp_crm.db"

Base = declarative_base()
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class HCPInteraction(Base):
    __tablename__ = "interactions"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, index=True)
    hcp_name = Column(String, index=True)
    specialty = Column(String)
    facility = Column(String)
    topic = Column(String)
    sentiment = Column(String)
    next_follow_up = Column(String)
    raw_log = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

def init_db():
    # Correct ORM function mapping call
    Base.metadata.create_all(bind=engine)