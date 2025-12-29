import requests
from config import GRAFANA_URL, GRAFANA_TOKEN


def grafana_health():
    r = requests.get(
        f"{GRAFANA_URL}/api/health",
        headers={
            "Authorization": f"Bearer {GRAFANA_TOKEN}"
        },
        timeout=5
    )
    r.raise_for_status()
    return r.json()

def list_dashboards():
    r = requests.get(
        f"{GRAFANA_URL}/api/search",
        headers={"Authorization": f"Bearer {GRAFANA_TOKEN}"},
        params={"type": "dash-db", "limit": 5000},
        timeout=10
    )
    r.raise_for_status()
    return r.json()

def get_dashboard(uid: str):
    r = requests.get(
        f"{GRAFANA_URL}/api/dashboards/uid/{uid}",
        headers={"Authorization": f"Bearer {GRAFANA_TOKEN}"},
        timeout=10
    )
    r.raise_for_status()
    return r.json()
