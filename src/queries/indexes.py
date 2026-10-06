"""
Index creation and Explain logic for MongoDB.
Requirement 1.1: 3 indexes (at least 1 compound).
Requirement 1.3: executionStats before/after + explanation.
"""
from pymongo import ASCENDING, DESCENDING
from config.settings import settings


def create_indexes(db):
    """Create required indexes on orders_validated."""
    coll = db[settings.VALIDATED_COLLECTION]

    # 1. Unique index on order_id (business key)
    coll.create_index([("order_id", ASCENDING)], unique=True, name="idx_order_id_unique")

    # 2. Single index on customer_id
    coll.create_index([("customer_id", ASCENDING)], name="idx_customer_id")

    # 3. Compound index (customer_id + order_date) for query + sort optimization
    coll.create_index(
        [("customer_id", ASCENDING), ("order_date", DESCENDING)],
        name="idx_customer_date_compound"
    )

    return ["idx_order_id_unique", "idx_customer_id", "idx_customer_date_compound"]


def explain_query(db, query, sort=None, label=""):
    """Run explain(executionStats) on a query and return stats."""
    coll = db[settings.VALIDATED_COLLECTION]
    cursor = coll.find(query)
    if sort:
        cursor = cursor.sort(sort)

    explain_result = cursor.explain()["executionStats"]
    stats = {
        "label": label,
        "query": str(query),
        "nReturned": explain_result.get("nReturned"),
        "totalDocsExamined": explain_result.get("totalDocsExamined"),
        "totalKeysExamined": explain_result.get("totalKeysExamined"),
        "executionTimeMillis": explain_result.get("executionTimeMillis"),
    }
    return stats


def run_explain_comparison(db, customer_id):
    """Run explain BEFORE and AFTER index creation."""
    query = {"customer_id": customer_id}
    sort = [("order_date", DESCENDING)]

    # BEFORE (ensure index doesn't exist yet in a fresh run)
    before = explain_query(db, query, sort, label="BEFORE_INDEX")

    # AFTER (create compound index)
    db[settings.VALIDATED_COLLECTION].create_index(
        [("customer_id", 1), ("order_date", -1)],
        name="idx_customer_date_compound"
    )
    after = explain_query(db, query, sort, label="AFTER_INDEX")

    return {"before": before, "after": after}
