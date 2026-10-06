"""
Materialized Views with INCREMENTAL update mechanism.
Requirement 3: 2 MVs + incremental refresh (no full rebuild).
"""
from datetime import datetime
from config.settings import settings


def get_state(db):
    return db["mv_state"]


def refresh_daily_sales_mv(db):
    """
    Incremental refresh of daily_sales_summary.
    Only processes records changed since last refresh using $merge.
    """
    state = get_state(db).find_one({"_id": settings.MV_DAILY_SALES})
    last_refresh = state["last_refresh"] if state else datetime(1970, 1, 1)

    pipeline = [
        {"$match": {"updated_at": {"$gt": last_refresh}}},
        {"$group": {
            "_id": {"$dateToString": {"format": "%Y-%m-%d", "date": "$order_date"}},
            "total_sales": {"$sum": "$total_amount"},
            "orders_count": {"$sum": 1},
            "avg_order_value": {"$avg": "$total_amount"}
        }},
        {"$project": {
            "_id": 0,
            "date": "$_id",
            "total_sales": 1,
            "orders_count": 1,
            "avg_order_value": 1
        }},
        # $merge with "whenMatched: merge" ADDS to existing values (incremental)
        {"$merge": {
            "into": settings.MV_DAILY_SALES,
            "on": "date",
            "whenMatched": [
                {"$set": {
                    "total_sales": {"$add": ["$total_sales", "$$new.total_sales"]},
                    "orders_count": {"$add": ["$orders_count", "$$new.orders_count"]},
                    "avg_order_value": "$$new.avg_order_value"
                }}
            ],
            "whenNotMatched": "insert"
        }}
    ]

    db[settings.VALIDATED_COLLECTION].aggregate(pipeline)

    get_state(db).update_one(
        {"_id": settings.MV_DAILY_SALES},
        {"$set": {"last_refresh": datetime.utcnow()}},
        upsert=True
    )
    return {"status": "success", "mv": settings.MV_DAILY_SALES}


def refresh_top_products_mv(db):
    """
    Incremental refresh of top_products_summary.
    """
    state = get_state(db).find_one({"_id": settings.MV_TOP_PRODUCTS})
    last_refresh = state["last_refresh"] if state else datetime(1970, 1, 1)

    pipeline = [
        {"$match": {"updated_at": {"$gt": last_refresh}}},
        {"$unwind": "$items"},
        {"$group": {
            "_id": "$items.product_id",
            "product_name": {"$first": "$items.product_name"},
            "total_quantity": {"$sum": "$items.quantity"},
            "total_revenue": {"$sum": {"$multiply": ["$items.quantity", "$items.price"]}}
        }},
        {"$project": {
            "_id": 0,
            "product_id": "$_id",
            "product_name": 1,
            "total_quantity": 1,
            "total_revenue": 1
        }},
        {"$merge": {
            "into": settings.MV_TOP_PRODUCTS,
            "on": "product_id",
            "whenMatched": [
                {"$set": {
                    "total_quantity": {"$add": ["$total_quantity", "$$new.total_quantity"]},
                    "total_revenue": {"$add": ["$total_revenue", "$$new.total_revenue"]},
                    "product_name": "$$new.product_name"
                }}
            ],
            "whenNotMatched": "insert"
        }}
    ]

    db[settings.VALIDATED_COLLECTION].aggregate(pipeline)

    get_state(db).update_one(
        {"_id": settings.MV_TOP_PRODUCTS},
        {"$set": {"last_refresh": datetime.utcnow()}},
        upsert=True
    )
    return {"status": "success", "mv": settings.MV_TOP_PRODUCTS}


ALL_MVS = {
    "daily_sales": refresh_daily_sales_mv,
    "top_products": refresh_top_products_mv,
}
