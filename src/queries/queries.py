"""
5 distinct queries on orders_validated.
Requirement 1.1: At least 5 queries.
"""
from datetime import datetime, timedelta
from config.settings import settings


def get_collection(db):
    return db[settings.VALIDATED_COLLECTION]


def query_top_customers_by_spend(db, limit=10):
    """Query 1: Highest spending customers."""
    pipeline = [
        {"$group": {"_id": "$customer_id", "total_spent": {"$sum": "$total_amount"}}},
        {"$sort": {"total_spent": -1}},
        {"$limit": limit},
    ]
    return list(get_collection(db).aggregate(pipeline))


def query_orders_by_date_range(db, start_date=None, end_date=None):
    """Query 2: Orders within a date range."""
    # Default to last 30 days if no dates provided
    if not end_date:
        end_date = datetime.utcnow()
    if not start_date:
        start_date = end_date - timedelta(days=30)

    return list(get_collection(db).find({
        "order_date": {"$gte": start_date, "$lte": end_date}
    }).limit(100))


def query_orders_by_status(db, status="pending"):
    """Query 3: Orders with specific status."""
    return list(get_collection(db).find({"status": status}).limit(100))


def query_high_value_orders(db, min_amount=1000):
    """Query 4: Orders above a value threshold."""
    return list(get_collection(db).find({"total_amount": {"$gte": min_amount}}).limit(100))


def query_customer_orders(db, customer_id="C001"):
    """Query 5: All orders for a specific customer (used with compound index)."""
    return list(
        get_collection(db)
        .find({"customer_id": customer_id})
        .sort("order_date", -1)
        .limit(100)
    )


# This is the dictionary that main.py imports
ALL_QUERIES = {
    "top_customers": query_top_customers_by_spend,
    "date_range": query_orders_by_date_range,
    "by_status": query_orders_by_status,
    "high_value": query_high_value_orders,
    "customer_orders": query_customer_orders,
}
