from datetime import datetime, timedelta

from sqlalchemy import case, func
from sqlalchemy.orm import Session

from app.models.exam_result import ExamResult
from app.models.exercise import Exercise
from app.models.passage import Passage
from app.models.sentence import Sentence
from app.models.study_record import StudyRecord
from app.models.word import Word
from app.models.wrong_item import WrongItem


def summary(db: Session, user_id: int, days: int) -> dict:
    since = datetime.utcnow() - timedelta(days=days)

    study_query = db.query(StudyRecord).filter(StudyRecord.user_id == user_id).filter(StudyRecord.created_at >= since)
    study_total = study_query.count()
    study_correct = study_query.filter(StudyRecord.correct.is_(True)).count()
    study_accuracy = (study_correct / study_total) if study_total > 0 else 0.0

    exam_query = db.query(ExamResult).filter(ExamResult.user_id == user_id).filter(ExamResult.created_at >= since)
    exam_total = exam_query.count()
    exam_avg_score = exam_query.with_entities(func.coalesce(func.avg(ExamResult.score), 0)).scalar() or 0
    exam_correct_sum, exam_total_sum = (
        exam_query.with_entities(
            func.coalesce(func.sum(ExamResult.correct), 0),
            func.coalesce(func.sum(ExamResult.total), 0),
        ).first()
        or (0, 0)
    )
    exam_correct_sum = int(exam_correct_sum or 0)
    exam_total_sum = int(exam_total_sum or 0)
    exam_accuracy = (exam_correct_sum / exam_total_sum) if exam_total_sum > 0 else 0.0

    if study_total == 0 and exam_total > 0:
        study_accuracy = exam_accuracy

    by_type_rows = (
        study_query.with_entities(
            StudyRecord.content_type,
            func.count(StudyRecord.id),
            func.sum(case((StudyRecord.correct.is_(True), 1), else_=0)),
        )
        .group_by(StudyRecord.content_type)
        .all()
    )
    by_type = []
    for content_type, total, correct in by_type_rows:
        total = int(total or 0)
        correct = int(correct or 0)
        accuracy = (correct / total) if total > 0 else 0.0
        by_type.append(
            {
                "content_type": content_type,
                "total": total,
                "correct": correct,
                "accuracy": round(accuracy, 4),
            }
        )

    by_exercise_type_rows = (
        study_query.join(Exercise, StudyRecord.content_id == Exercise.id)
        .filter(StudyRecord.content_type == "exercise")
        .with_entities(
            Exercise.exercise_type,
            func.count(StudyRecord.id),
            func.sum(case((StudyRecord.correct.is_(True), 1), else_=0)),
        )
        .group_by(Exercise.exercise_type)
        .all()
    )
    by_exercise_type = []
    for exercise_type, total, correct in by_exercise_type_rows:
        total = int(total or 0)
        correct = int(correct or 0)
        accuracy = (correct / total) if total > 0 else 0.0
        by_exercise_type.append(
            {
                "content_type": exercise_type,
                "total": total,
                "correct": correct,
                "accuracy": round(accuracy, 4),
            }
        )

    weak_items = (
        db.query(WrongItem)
        .filter(WrongItem.user_id == user_id)
        .order_by(WrongItem.wrong_count.desc(), WrongItem.last_wrong_at.desc())
        .limit(5)
        .all()
    )
    weak = [
        {
            "content_type": item.content_type,
            "content_id": item.content_id,
            "wrong_count": item.wrong_count,
        }
        for item in weak_items
    ]

    level_rows = (
        study_query.with_entities(
            StudyRecord.content_type,
            StudyRecord.content_id,
            func.sum(case((StudyRecord.correct.is_(True), 1), else_=0)).label("correct"),
            func.count(StudyRecord.id).label("total"),
        )
        .group_by(StudyRecord.content_type, StudyRecord.content_id)
        .all()
    )
    level_stats: dict[str, dict[str, int]] = {}
    for ctype, content_id, correct_count, total_count in level_rows:
        if ctype != "exercise":
            continue
        exercise = db.get(Exercise, content_id)
        if exercise is None or not exercise.level:
            continue
        level = exercise.level
        entry = level_stats.setdefault(level, {"total": 0, "correct": 0})
        entry["total"] += int(total_count or 0)
        entry["correct"] += int(correct_count or 0)
    by_level = []
    for level, stats in level_stats.items():
        total = stats["total"]
        correct = stats["correct"]
        accuracy = (correct / total) if total > 0 else 0.0
        by_level.append({"level": level, "total": total, "correct": correct, "accuracy": round(accuracy, 4)})

    suggestions = []
    if study_accuracy < 0.6:
        suggestions.append("加强基础练习，优先完成 A1/A2 词句训练。")
    if exam_avg_score < 60:
        suggestions.append("建议每周至少完成 2 次模拟考试并复盘错题。")
    if weak_items:
        suggestions.append("针对错题本中的高频错误内容进行专项复习。")

    return {
        "study_total": study_total,
        "study_accuracy": round(study_accuracy, 4),
        "exam_total": exam_total,
        "exam_avg_score": round(float(exam_avg_score), 2),
        "weak_items": weak,
        "by_type": by_type,
        "by_exercise_type": by_exercise_type,
        "by_level": by_level,
        "suggestions": suggestions,
    }


def trend(db: Session, user_id: int, days: int) -> list[dict]:
    since = datetime.utcnow() - timedelta(days=days)
    rows = (
        db.query(
            func.date_trunc("day", StudyRecord.created_at).label("day"),
            func.count(StudyRecord.id).label("total"),
            func.sum(case((StudyRecord.correct.is_(True), 1), else_=0)).label("correct"),
        )
        .filter(StudyRecord.user_id == user_id)
        .filter(StudyRecord.created_at >= since)
        .group_by("day")
        .order_by("day")
        .all()
    )
    results = []
    for day, total, correct in rows:
        total = int(total or 0)
        correct = int(correct or 0)
        accuracy = (correct / total) if total > 0 else 0.0
        results.append(
            {
                "date": day.date().isoformat(),
                "total": total,
                "correct": correct,
                "accuracy": round(accuracy, 4),
            }
        )
    return results


def trend_by_type(db: Session, user_id: int, days: int) -> list[dict]:
    since = datetime.utcnow() - timedelta(days=days)
    rows = (
        db.query(
            func.date_trunc("day", StudyRecord.created_at).label("day"),
            StudyRecord.content_type,
            func.count(StudyRecord.id).label("total"),
            func.sum(case((StudyRecord.correct.is_(True), 1), else_=0)).label("correct"),
        )
        .filter(StudyRecord.user_id == user_id)
        .filter(StudyRecord.created_at >= since)
        .group_by("day", StudyRecord.content_type)
        .order_by("day")
        .all()
    )
    results = []
    for day, content_type, total, correct in rows:
        total = int(total or 0)
        correct = int(correct or 0)
        accuracy = (correct / total) if total > 0 else 0.0
        results.append(
            {
                "date": day.date().isoformat(),
                "content_type": content_type,
                "total": total,
                "correct": correct,
                "accuracy": round(accuracy, 4),
            }
        )
    return results


def recommendations(db: Session, user_id: int, limit: int) -> list[dict]:
    items = (
        db.query(WrongItem)
        .filter(WrongItem.user_id == user_id)
        .order_by(WrongItem.wrong_count.desc(), WrongItem.last_wrong_at.desc())
        .limit(limit)
        .all()
    )
    results = []
    for item in items:
        preview = None
        link = None
        if item.content_type == "word":
            word = db.get(Word, item.content_id)
            if word is not None:
                preview = f"{word.text} - {word.meaning}"
                link = f"/words/{word.id}"
        elif item.content_type == "sentence":
            sentence = db.get(Sentence, item.content_id)
            if sentence is not None:
                preview = sentence.text
                link = f"/sentences/{sentence.id}"
        elif item.content_type == "passage":
            passage = db.get(Passage, item.content_id)
            if passage is not None:
                preview = passage.title
                link = f"/passages/{passage.id}"
        elif item.content_type == "exercise":
            exercise = db.get(Exercise, item.content_id)
            if exercise is not None:
                preview = exercise.prompt
                link = f"/exercises/{exercise.id}"
        results.append(
            {
                "content_type": item.content_type,
                "content_id": item.content_id,
                "reason": "高频错题，建议优先复习",
                "preview": preview,
                "link": link,
            }
        )
    return results
