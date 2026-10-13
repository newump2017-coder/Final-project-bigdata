from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional

from config.settings import settings
from src.db import MongoManager
# FIX: Ensure this import exactly matches the file structure
from src.queries.queries import ALL_QUERIES
from src.queries.indexes import create_indexes, run_explain_comparison
from src.aggregations.aggregations import ALL_AGGREGATIONS
from src.mv.materialized_views import ALL_MVS
from src.jobs.scheduler import JOBS, _run_job

app = FastAPI(
    title="Big Data Pipeline API",
    description="Unified API for the Big Data Project Phase 2",
    version="1.0.0"
)


# ---------- Request Models ----------
class IngestRequest(BaseModel):
    file_path: str


class ExplainRequest(BaseModel):
    customer_id: str


# ---------- Endpoints ----------
@app.get("/health")
def health():
    return {"status": "ok", "service": "bigdata-api"}


@app.post("/ingest")
def ingest(req: IngestRequest):
    try:
        from src.ingestion.pipeline import run_pipeline
        result = run_pipeline(req.file_path)
        return {"status": "success", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/indexes")
def build_indexes():
    with MongoManager() as db:
        created = create_indexes(db)
    return {"status": "success", "indexes": created}


@app.post("/indexes/explain")
def explain_indexes(req: ExplainRequest):
    with MongoManager() as db:
        result = run_explain_comparison(db, req.customer_id)
    return result


@app.get("/queries")
def list_queries():
    # Return the keys of the ALL_QUERIES dictionary
    return {"queries": list(ALL_QUERIES.keys())}


@app.get("/queries/{name}")
def run_query(name: str):
    if name not in ALL_QUERIES:
        raise HTTPException(404, f"Unknown query: {name}")

    fn = ALL_QUERIES[name]
    with MongoManager() as db:
        try:
            # Call the function with default arguments
            result = fn(db)
        except Exception as e:
            raise HTTPException(500, f"Error executing query {name}: {str(e)}")

    return {"query": name, "count": len(result), "result": result}


@app.get("/aggregations")
def list_aggregations():
    return {"aggregations": list(ALL_AGGREGATIONS.keys())}


@app.get("/aggregations/{name}")
def run_aggregation(name: str):
    if name not in ALL_AGGREGATIONS:
        raise HTTPException(404, f"Unknown aggregation: {name}")
    fn = ALL_AGGREGATIONS[name]
    with MongoManager() as db:
        result = fn(db)
    return {"aggregation": name, "count": len(result), "result": result}


@app.post("/refresh-mv")
def refresh_mv(mv: Optional[str] = None):
    results = {}
    with MongoManager() as db:
        if mv:
            if mv not in ALL_MVS:
                raise HTTPException(404, f"Unknown MV: {mv}")
            results[mv] = ALL_MVS[mv](db)
        else:
            for name, fn in ALL_MVS.items():
                results[name] = fn(db)
    return {"status": "success", "results": results}


@app.get("/jobs")
def list_jobs():
    return {"jobs": list(JOBS.keys())}


@app.post("/jobs/{name}/run")
def run_job(name: str, bg: BackgroundTasks):
    if name not in JOBS:
        raise HTTPException(404, f"Unknown job: {name}")
    bg.add_task(JOBS[name])
    return {"status": "scheduled", "job": name}
