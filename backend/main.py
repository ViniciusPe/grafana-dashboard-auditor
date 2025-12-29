from fastapi import FastAPI
from config import GRAFANA_URL, DB_HOST, DB_NAME
from removal_audit import get_recommended_for_removal
from analyzer import find_broken_dashboards
from access_audit import dashboards_not_viewed
from access_tracking import track_dashboard_access, get_most_accessed
from usage_analyzer import get_dashboards_by_usage

app = FastAPI(title="Grafana Dashboard Auditor")

from fastapi.middleware.cors import CORSMiddleware


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)


@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/config-check")
def config_check():
    return {
        "grafana_url": GRAFANA_URL,
        "db_host": DB_HOST,
        "db_name": DB_NAME
    }

@app.get("/grafana-health")
def grafana_health_check():
    return {"status": "ok", "grafana_url": GRAFANA_URL}

@app.get("/audit/broken-dashboards")
def audit_broken():
    return find_broken_dashboards()

@app.get("/audit/unused-dashboards")
def audit_unused(days: int = 30):
    return dashboards_not_viewed(days)

@app.post("/track/dashboard-access")
def track_access(payload: dict):
    uid = payload.get("dashboard_uid")
    if not uid:
        return {"error": "dashboard_uid is required"}
    track_dashboard_access(uid)
    return {"status": "ok"}

@app.get("/audit/most-accessed-dashboards")
def most_accessed(limit: int = 10):
    return get_most_accessed(limit)

@app.get("/audit/recommended-for-removal")
def recommended_for_removal(days: int = 15):
    return get_recommended_for_removal(days)

@app.get("/audit/usage-report")
def usage_report(periods: str = "1,3,7,30"):
    days_list = [int(x.strip()) for x in periods.split(",")]
    return get_dashboards_by_usage(days_list)
