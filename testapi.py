import requests
import json

BASE_URL = "http://localhost:8000"

def test_health():
    r = requests.get(f"{BASE_URL}/health")
    print("HEALTH:", r.status_code, r.json())

def test_queries():
    r = requests.get(f"{BASE_URL}/queries")
    print("LIST QUERIES:", r.status_code, r.json())

    # Test one specific query
    r = requests.get(f"{BASE_URL}/queries/top_customers")
    print("RUN top_customers:", r.status_code, r.json().get("count", 0), "results")

if __name__ == "__main__":
    print("Testing API...")
    test_health()
    test_queries()
    print("Done.")
