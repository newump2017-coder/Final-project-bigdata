"""
Scheduled jobs using APScheduler.
Requirement 4: 2 jobs, log execution, run on schedule.
"""
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
from config.settings import settings
from src.db import MongoManager
from src.mv.materialized_views import refresh_daily_sales_mv, refresh_top_products_mv


def _log_execution(job_name, status, error=None, duration=None):
    """Insert job execution log into MongoDB."""
    with MongoManager() as db:
        db[settings.JOBS_LOG_COLLECTION].insert_one({
            "job_name": job_name,
            "start_time": datetime.utcnow(),
            "status": status,
            "error": error,
            "duration_seconds": duration
        })


def _run_job(job_name, fn, **kwargs):
    start = datetime.utcnow()
    try:
        with MongoManager() as db:
            fn(db, **kwargs)
        _log_execution(job_name, "SUCCESS", duration=(datetime.utcnow() - start).total_seconds())
    except Exception as e:
        _log_execution(job_name, "FAILED", error=str(e),
                       duration=(datetime.utcnow() - start).total_seconds())


def job_refresh_daily_sales():
    _run_job("refresh_daily_sales_mv", refresh_daily_sales_mv)


def job_refresh_top_products():
    _run_job("refresh_top_products_mv", refresh_top_products_mv)


JOBS = {
    "refresh_daily_sales_mv": job_refresh_daily_sales,
    "refresh_top_products_mv": job_refresh_top_products,
}


def start_scheduler():
    scheduler = BackgroundScheduler()
    # Job 1: every hour
    scheduler.add_job(job_refresh_daily_sales, "interval", hours=1,
                      id="refresh_daily_sales_mv")
    # Job 2: every day at midnight
    scheduler.add_job(job_refresh_top_products, "cron", hour=0, minute=0,
                      id="refresh_top_products_mv")
    scheduler.start()
    return scheduler
