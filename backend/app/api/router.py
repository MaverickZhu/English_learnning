from fastapi import APIRouter

from app.api.routes import admin, audit, auth, exam, exercises, health, mastery, mistake, news, news_public, passages, plan, practice, progress, report, review, sentences, words

api_router = APIRouter()

api_router.include_router(health.router, tags=["health"])
api_router.include_router(words.router, tags=["words"])
api_router.include_router(sentences.router, tags=["sentences"])
api_router.include_router(passages.router, tags=["passages"])
api_router.include_router(exercises.router, tags=["exercises"])
api_router.include_router(admin.router, tags=["admin"])
api_router.include_router(news.router, tags=["admin-news"])
api_router.include_router(news_public.router, tags=["news"])
api_router.include_router(audit.router, tags=["admin-audit"])
api_router.include_router(auth.router, tags=["auth"])
api_router.include_router(practice.router, tags=["practice"])
api_router.include_router(progress.router, tags=["progress"])
api_router.include_router(plan.router, tags=["plans"])
api_router.include_router(review.router, tags=["review"])
api_router.include_router(mistake.router, tags=["mistakes"])
api_router.include_router(mastery.router, tags=["mastery"])
api_router.include_router(exam.router, tags=["exam"])
api_router.include_router(report.router, tags=["reports"])
