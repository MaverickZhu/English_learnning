from apscheduler.schedulers.background import BackgroundScheduler

scheduler = BackgroundScheduler(timezone="UTC")


def start_scheduler() -> None:
    if scheduler.running:
        return
    scheduler.start()


def schedule_daily_job(job_func, hour: int, minute: int) -> None:
    scheduler.add_job(job_func, "cron", hour=hour, minute=minute, id="news_ingest_daily", replace_existing=True)
