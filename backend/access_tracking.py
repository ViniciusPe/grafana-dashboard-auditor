from db import get_conn

def track_dashboard_access(dashboard_uid: str):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO auditor.dashboard_access_stats (dashboard_uid, access_count, last_access)
        VALUES (%s, 1, NOW())
        ON CONFLICT (dashboard_uid)
        DO UPDATE SET
            access_count = auditor.dashboard_access_stats.access_count + 1,
            last_access = NOW();
    """, (dashboard_uid,))
    conn.commit()
    cur.close()
    conn.close()

def get_most_accessed(limit: int = 10):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        SELECT dashboard_uid, access_count, last_access
        FROM auditor.dashboard_access_stats
        ORDER BY access_count DESC NULLS LAST
        LIMIT %s;
    """, (limit,))
    rows = cur.fetchall()
    cur.close()
    conn.close()

    result = []
    for r in rows:
        result.append({
            "uid": r[0],
            "title": r[0],
            "access_count": r[1],
            "last_access": r[2],
            "reason": "Most accessed"
        })
    return result
