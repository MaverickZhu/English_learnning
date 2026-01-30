from sqlalchemy.orm import Session

from app.models.exam_config import ExamConfig


def create_config(db: Session, payload: dict) -> ExamConfig:
    config = ExamConfig(**payload)
    db.add(config)
    db.commit()
    db.refresh(config)
    return config


def get_config_by_name(db: Session, name: str) -> ExamConfig | None:
    return db.query(ExamConfig).filter(ExamConfig.name == name).first()


def list_configs(db: Session) -> list[ExamConfig]:
    return db.query(ExamConfig).order_by(ExamConfig.id.desc()).all()
