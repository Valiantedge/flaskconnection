from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True)
    password = Column(String(128))

class Agent(Base):
    __tablename__ = 'agents'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True)
    token = Column(String(128), unique=True)
    status = Column(String(20), default='inactive')
    last_heartbeat = Column(DateTime, default=datetime.utcnow)
    customer_id = Column(Integer, nullable=True, index=True)
    cluster_id = Column(Integer, nullable=True, index=True)

class Command(Base):
    __tablename__ = 'commands'
    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(Integer, ForeignKey('agents.id'))
    command = Column(Text)
    status = Column(String(20), default='queued')
    output = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
