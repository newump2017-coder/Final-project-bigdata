# Big Data Project – Phase 2 (Final)

Hybrid data pipeline (Python Batch + PySpark) with ELT principles, MongoDB storage,
unified FastAPI interface, and incremental Materialized Views.

## 1. Installation

```bash
git clone <your-repo-url>
cd <repo>
python -m venv .venv
source .venv/bin/activate     # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## 2. Configuration

Copy the template and adjust:

```bash
cp .env.example .env
```

Variables:
- `MONGODB_URI` – MongoDB connection string
- `DB_NAME` – Database name
- `SMALL_FILE_THRESHOLD_MB` – Router threshold (default 200)
- `BATCH_SIZE` – Python batch size

## 3. Run the Pipeline (Midterm)

```bash
python -m src.ingestion.pipeline --file data/sample.csv
```

The File Router picks:
- `python_batch` if file ≤ `SMALL_FILE_THRESHOLD_MB`
- `pyspark` otherwise

## 4. Run the API (Phase 2)

```bash
python -m src.main
```

Swagger UI: `http://localhost:8000/docs`

### Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET  | `/health` | Health check |
| POST | `/ingest` | Run ingestion pipeline |
| POST | `/indexes` | Create indexes |
| POST | `/indexes/explain` | executionStats before/after |
| GET  | `/queries` | List queries |
| GET  | `/queries/{name}` | Run a query |
| GET  | `/aggregations` | List aggregations |
| GET  | `/aggregations/{name}` | Run an aggregation |
| POST | `/refresh-mv` | Refresh Materialized Views |
| GET  | `/jobs` | List scheduled jobs |
| POST | `/jobs/{name}/run` | Manually run a job |

## 5. Indexes & Explain

5 queries + 3 indexes (1 compound) implemented. Explain comparison is
available via `POST /indexes/explain` with body `{"customer_id": "C001"}`.

## 6. Aggregations

5 aggregation pipelines: `daily_sales`, `top_products`, `best_customers`,
`sales_by_region`, `order_status`.

## 7. Materialized Views (Incremental)

Two MVs: `daily_sales_summary`, `top_products_summary`.
Refreshed incrementally using `$merge` (never full rebuild) and tracked in `mv_state`.

## 8. Scheduled Jobs

- `refresh_daily_sales_mv` – every hour
- `refresh_top_products_mv` – daily at 00:00

All executions logged in `jobs_log` collection.

## 9. Tests

```bash
pytest tests/
```

## 10. Project Structure

```
project-root/
├── config/settings.py
├── src/
│   ├── db.py
│   ├── api/main.py
│   ├── queries/{queries.py, indexes.py}
│   ├── aggregations/aggregations.py
│   ├── mv/materialized_views.py
│   ├── jobs/scheduler.py
│   ├── ingestion/pipeline.py
│   └── main.py
├── tests/
├── reports/
├── requirements.txt
├── .env.example
└── README.md
```



# Start API
python -m src.main

# In another terminal:
curl http://localhost:8000/health
curl -X POST http://localhost:8000/indexes
curl http://localhost:8000/queries
curl http://localhost:8000/queries/top_customers
curl http://localhost:8000/aggregations/daily_sales
curl -X POST http://localhost:8000/refresh-mv
curl http://localhost:8000/jobs
curl -X POST http://localhost:8000/jobs/refresh_daily_sales_mv/run
