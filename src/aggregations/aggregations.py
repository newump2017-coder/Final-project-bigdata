"""
5 MongoDB Aggregation pipelines.
Requirement 2: At least 5 aggregation reports.
"""
from config.settings import settings


def get_collection(db):
    return db[settings.VALIDATED_COLLECTION]


def agg_daily_sales(db):
    """Aggregation 1: Daily sales summary."""
    pipeline = [
        {"$group": {
            "_id": {"$dateToString": {"format": "%Y-%m-%d", "date": "$order_date"}},
            "total_sales": {"$sum": "$total_amount"},
            "orders_count": {"$sum": 1},
            "avg_order_value": {"$avg": "$total_amount"}
        }},
        {"$sort": {"_id": 1}}
    ]
    return list(get_collection(db).aggregate(pipeline))


def agg_top_products(db, limit=10):
    """Aggregation 2: Best-selling products (unwind items)."""
    pipeline = [
        {"$unwind": "$items"},
        {"$group": {
            "_id": "$items.product_id",
            "total_quantity": {"$sum": "$items.quantity"},
            "total_revenue": {"$sum": {"$multiply": ["$items.quantity", "$items.price"]}}
        }},
        {"$sort": {"total_quantity": -1}},
        {"$limit": limit}
    ]
    return list(get_collection(db).aggregate(pipeline))


def agg_best_customers(db, limit=10):
    """Aggregation 3: Best customers by orders count."""
    pipeline = [
        {"$group": {
            "_id": "$customer_id",
            "orders_count": {"$sum": 1},
            "total_spent": {"$sum": "$total_amount"}
        }},
        {"$sort": {"orders_count": -1}},
        {"$limit": limit}
    ]
    return list(get_collection(db).aggregate(pipeline))


def agg_sales_by_region(db):
    """Aggregation 4: Sales grouped by region."""
    pipeline = [
        {"$group": {
            "_id": "$customer_region",
            "total_sales": {"$sum": "$total_amount"},
            "orders_count": {"$sum": 1}
        }},
        {"$sort": {"total_sales": -1}}
    ]
    return list(get_collection(db).aggregate(pipeline))


def agg_order_status_distribution(db):
    """Aggregation 5: Distribution of order status."""
    pipeline = [
        {"$group": {
            "_id": "$status",
            "count": {"$sum": 1},
            "total_amount": {"$sum": "$total_amount"}
        }},
        {"$sort": {"count": -1}}
    ]
    return list(get_collection(db).aggregate(pipeline))


ALL_AGGREGATIONS = {
    "daily_sales": agg_daily_sales,
    "top_products": agg_top_products,
    "best_customers": agg_best_customers,
    "sales_by_region": agg_sales_by_region,
    "order_status": agg_order_status_distribution,
}
