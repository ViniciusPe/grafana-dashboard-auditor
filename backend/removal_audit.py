from datetime import datetime, timedelta, timezone
from grafana_api import list_dashboards
from analyzer import find_broken_dashboards
from db import get_conn

def get_recommended_for_removal(days: int = 15):
    removal_candidates = []

    broken_list = find_broken_dashboards()
    for b in broken_list:
        removal_candidates.append({
            "uid": b["uid"],
            "title": b["title"],
            "access_count": None,
            "last_access": None,
            "reason": f"Broken dashboard ({b['reason']})"
        })

    try:
        conn = get_conn()
        cur = conn.cursor()

        since = datetime.now(timezone.utc) - timedelta(days=days)

        cur.execute("""
            SELECT dashboard_uid, access_count, last_access
            FROM auditor.dashboard_access_stats
            WHERE last_access IS NULL
               OR last_access < %s
        """, (since,))

        rows = cur.fetchall()
        cur.close()
        conn.close()

        for r in rows:
            uid, count, last = r
            if any(d["uid"] == uid for d in removal_candidates):
                continue

            removal_candidates.append({
                "uid": uid,
                "title": uid,
                "access_count": count,
                "last_access": last,
                "reason": f"Inactive for more than {days} days"
            })

    except Exception as e:
        removal_candidates.append({"error": str(e)})

    return removal_candidates

def get_all_removal_candidates(days: int = 15):
    candidates = []

    broken = find_broken_dashboards()
    for b in broken:
        candidates.append({
            "uid": b["uid"],
            "title": b["title"],
            "access_count": None,
            "last_access": None,
            "reason": f"Broken dashboard ({b['reason']})"
        })

    inactive = []
    try:
        conn = get_conn()
        cur = conn.cursor()
        since = datetime.now(timezone.utc) - timedelta(days=days)
        cur.execute("""
            SELECT dashboard_uid, access_count, last_access
            FROM auditor.dashboard_access_stats
            WHERE last_access IS NULL
               OR last_access < %s
        """, (since,))
        rows = cur.fetchall()
        cur.close()
        conn.close()
        for r in rows:
            inactive.append({"uid": r[0], "access_count": r[1], "last_access": r[2]})
    except:
        pass

    for i in inactive:
        if any(c["uid"] == i["uid"] for c in candidates):
            continue
        candidates.append({
            "uid": i["uid"],
            "title": i["uid"],
            "access_count": i.get("access_count"),
            "last_access": i.get("last_access"),
            "reason": f"Inactive for more than {days} days"
        })

    return candidates
