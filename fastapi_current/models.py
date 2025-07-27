from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Customer(Base):
    __tablename__ = 'customers'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, index=True)
    # Add more fields as needed (email, address, etc.)


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True)
    password = Column(String(128))
    customer_id = Column(Integer, ForeignKey('customers.id'))


class Workspace(Base):
    __tablename__ = 'workspaces'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, index=True)
    customer_id = Column(Integer, index=True)

class Environment(Base):
    __tablename__ = 'environments'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), index=True)
    workspace_id = Column(Integer, ForeignKey('workspaces.id'))

    # Modifications to the Agent class
class Agent(Base):
    __tablename__ = 'agents'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True)
    token = Column(String(128), unique=True)
    status = Column(String(20), default='inactive')
    last_heartbeat = Column(DateTime, default=datetime.utcnow)
    customer_id = Column(Integer, nullable=True, index=True)
    cluster_id = Column(Integer, nullable=True, index=True)
    workspace_id = Column(Integer, ForeignKey('workspaces.id'), nullable=True, index=True)
    environment_id = Column(Integer, ForeignKey('environments.id'), nullable=True, index=True)
    ip_address = Column(String(45), nullable=True, index=True)  # IPv6 max length
    machine_uuid = Column(String(64), nullable=True, index=True)
    os_type = Column(String(32), nullable=True, index=True)
class Command(Base):
    __tablename__ = 'commands'
    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(Integer, ForeignKey('agents.id'))
    command = Column(Text)
    status = Column(String(20), default='queued')
    output = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
