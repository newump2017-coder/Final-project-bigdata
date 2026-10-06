import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
    DB_NAME = os.getenv("DB_NAME", "bigdata_project")

    RAW_COLLECTION = os.getenv("RAW_COLLECTION", "orders_raw")
    VALIDATED_COLLECTION = os.getenv("VALIDATED_COLLECTION", "orders_validated")
    QUARANTINE_COLLECTION = os.getenv("QUARANTINE_COLLECTION", "orders_quarantine")

    MV_DAILY_SALES = os.getenv("MV_DAILY_SALES", "daily_sales_summary")
    MV_TOP_PRODUCTS = os.getenv("MV_TOP_PRODUCTS", "top_products_summary")
    JOBS_LOG_COLLECTION = os.getenv("JOBS_LOG_COLLECTION", "jobs_log")

    SMALL_FILE_THRESHOLD_MB = int(os.getenv("SMALL_FILE_THRESHOLD_MB", 200))
    BATCH_SIZE = int(os.getenv("BATCH_SIZE", 1000))

    API_HOST = os.getenv("API_HOST", "0.0.0.0")
    API_PORT = int(os.getenv("API_PORT", 8000))


settings = Settings()
