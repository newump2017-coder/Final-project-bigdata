import uvicorn
from config.settings import settings
from src.api.main import app
from src.jobs.scheduler import start_scheduler


if __name__ == "__main__":
    scheduler = start_scheduler()
    try:
        uvicorn.run(app, host=settings.API_HOST, port=settings.API_PORT)
    finally:
        scheduler.shutdown()
