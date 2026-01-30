from app.crud.base import CRUDBase
from app.crud.content import exercise_crud, passage_crud, sentence_crud, word_crud
from app.crud.exam_result import create_result, list_results
from app.crud.exam_config import create_config, get_config_by_name
from app.crud.exam import generate_exam, get_exam
from app.crud.mistake import list_mistakes, record_mistake
from app.crud.mastery import mastery_summary
from app.crud.report import recommendations as report_recommendations
from app.crud.report import summary as report_summary
from app.crud.report import trend as report_trend
from app.crud.report import trend_by_type as report_trend_by_type
from app.crud.plan import activate_plan, create_plan, get_active_plan, list_plans
from app.crud.progress import create_record, list_records, summary
from app.crud.review import create_reminder, list_reminders, mark_done
from app.crud.user import create_user, get_user_by_email

__all__ = [
    "CRUDBase",
    "create_user",
    "exercise_crud",
    "get_user_by_email",
    "generate_exam",
    "get_exam",
    "create_result",
    "list_results",
    "create_config",
    "get_config_by_name",
    "create_record",
    "list_records",
    "summary",
    "list_mistakes",
    "record_mistake",
    "mastery_summary",
    "report_trend",
    "report_trend_by_type",
    "report_summary",
    "report_recommendations",
    "create_plan",
    "list_plans",
    "activate_plan",
    "get_active_plan",
    "create_reminder",
    "list_reminders",
    "mark_done",
    "passage_crud",
    "sentence_crud",
    "word_crud",
]