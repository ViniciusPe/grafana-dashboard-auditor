from datetime import datetime, timedelta, timezone
from db import get_conn

def get_dashboards_by_usage(days_list):
    result = []

    for days in days_list:
        conn = get_conn()
        cur = conn.cursor()
        since = datetime.now(timezone.utc) - timedelta(days=days)

        cur.execute("""
            SELECT dvs.dashboard_uid, d.title, dvs.access_count, dvs.last_access
            FROM auditor.dashboard_access_stats dvs
            LEFT JOIN dashboard d ON d.uid = dvs.dashboard_uid
            WHERE dvs.last_access IS NULL OR dvs.last_access < %s
            ORDER BY dvs.last_access ASC NULLS FIRST
        """, (since,))

        rows = cur.fetchall()
        cur.close()
        conn.close()

        dashboards = []
        for uid, title, count, last in rows:
            dashboards.append({
                "uid": uid,
                "title": title or uid,
                "access_count": count,
                "last_access": last,
                "reason": "Never accessed" if last is None else f"Not accessed in last {days} days"
            })

        result.append({
            "period_days": days,
            "dashboards": dashboards
        })

    return result
