from sqlalchemy.orm import Session

from app.models.study_plan import StudyPlan


def create_plan(db: Session, payload: dict) -> StudyPlan:
    plan = StudyPlan(**payload)
    db.add(plan)
    db.commit()
    db.refresh(plan)
    return plan


def list_plans(db: Session, user_id: int) -> list[StudyPlan]:
    return db.query(StudyPlan).filter(StudyPlan.user_id == user_id).order_by(StudyPlan.id.desc()).all()


def activate_plan(db: Session, plan_id: int) -> StudyPlan | None:
    plan = db.get(StudyPlan, plan_id)
    if plan is None:
        return None
    db.query(StudyPlan).filter(StudyPlan.user_id == plan.user_id).update({"is_active": False})
    plan.is_active = True
    db.add(plan)
    db.commit()
    db.refresh(plan)
    return plan


def get_active_plan(db: Session, user_id: int) -> StudyPlan | None:
    return db.query(StudyPlan).filter(StudyPlan.user_id == user_id).filter(StudyPlan.is_active.is_(True)).first()
