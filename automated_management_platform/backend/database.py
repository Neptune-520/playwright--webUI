import os
from datetime import datetime
from sqlalchemy import create_engine, Column, String, Integer, Float, Text, DateTime, JSON, ForeignKey, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./automated_management.db")

engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Folder(Base):
    __tablename__ = "folders"

    id = Column(String(36), primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


class ScriptResult(Base):
    __tablename__ = "script_results"

    id = Column(String(36), primary_key=True, index=True)
    task_id = Column(Integer, nullable=False, index=True)
    task_name = Column(String(255), nullable=False, index=True)
    script_name = Column(String(255), nullable=False, index=True)
    started_at = Column(String(50), nullable=False, index=True)
    finished_at = Column(String(50), nullable=False)
    status = Column(String(50), nullable=False, index=True)
    parameters = Column(JSON, default=dict)
    total_steps = Column(Integer, nullable=False)
    passed_steps = Column(Integer, nullable=False)
    failed_steps = Column(Integer, nullable=False)
    skipped_steps = Column(Integer, nullable=False)
    total_duration = Column(Float, nullable=False)
    pass_rate = Column(Float, nullable=False)
    username = Column(String(100), nullable=True, default="", index=True)
    script_count = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    step_results = relationship("StepResultModel", back_populates="script_result", cascade="all, delete-orphan", lazy="joined")

    def to_dict(self):
        return {
            "id": self.id,
            "task_id": self.task_id,
            "task_name": self.task_name,
            "script_name": self.script_name,
            "started_at": self.started_at,
            "finished_at": self.finished_at,
            "status": self.status,
            "parameters": self.parameters or {},
            "total_steps": self.total_steps,
            "passed_steps": self.passed_steps,
            "failed_steps": self.failed_steps,
            "skipped_steps": self.skipped_steps,
            "total_duration": self.total_duration,
            "pass_rate": self.pass_rate,
            "username": self.username or "",
            "script_count": self.script_count,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "step_results": [step.to_dict() for step in self.step_results]
        }

    __table_args__ = (
        Index('idx_script_results_status', 'status'),
        Index('idx_script_results_started_at', 'started_at'),
        Index('idx_script_results_username', 'username'),
        Index('idx_script_results_task_name', 'task_name'),
        Index('idx_script_results_created_at', 'created_at'),
    )


class StepResultModel(Base):
    __tablename__ = "step_results"

    id = Column(String(36), primary_key=True, index=True)
    script_result_id = Column(String(36), ForeignKey("script_results.id", ondelete="CASCADE"), nullable=False, index=True)
    step_name = Column(String(255), nullable=False, index=True)
    step_order = Column(Integer, nullable=False)
    action_type = Column(String(100), nullable=False)
    status = Column(String(50), nullable=False, index=True)
    duration = Column(Float, nullable=False)
    error = Column(Text, nullable=True)
    error_stack = Column(Text, nullable=True)
    screenshot = Column(String(500), nullable=True)
    action_values = Column(JSON, default=dict)

    script_result = relationship("ScriptResult", back_populates="step_results")

    def to_dict(self):
        return {
            "id": self.id,
            "script_result_id": self.script_result_id,
            "step_name": self.step_name,
            "step_order": self.step_order,
            "action_type": self.action_type,
            "status": self.status,
            "duration": self.duration,
            "error": self.error,
            "error_stack": self.error_stack,
            "screenshot": self.screenshot,
            "action_values": self.action_values or {}
        }

    __table_args__ = (
        Index('idx_step_results_status', 'status'),
        Index('idx_step_results_step_name', 'step_name'),
    )


class Config(Base):
    __tablename__ = "config"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(100), nullable=False, unique=True, index=True)
    value = Column(JSON, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "key": self.key,
            "value": self.value,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }


def init_db():
    Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
