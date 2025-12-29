from datetime import datetime, timedelta
from db import get_conn


def dashboards_not_viewed(days: int = 30):
    """
    Retorna dashboards que:
    - nunca foram acessados (não existem em auditor.dashboard_access_stats)
    OU
    - não são acessados há mais de X dias
    """

    since = datetime.utcnow() - timedelta(days=days)

    conn = get_conn()
    cur = conn.cursor()

    query = """
    SELECT
        d.uid,
        d.title,
        s.access_count,
        s.last_access
    FROM dashboard d
    LEFT JOIN auditor.dashboard_access_stats s
        ON s.dashboard_uid = d.uid
    WHERE
        s.dashboard_uid IS NULL
        OR s.last_access < %s
    ORDER BY
        s.last_access NULLS FIRST;
    """

    cur.execute(query, (since,))
    rows = cur.fetchall()

    result = []
    for uid, title, access_count, last_access in rows:
        if last_access is None:
            reason = "Never accessed"
        else:
            reason = f"Not accessed in last {days} days"

        result.append({
            "uid": uid,
            "title": title,
            "access_count": access_count or 0,
            "last_access": last_access,
            "reason": reason
        })

    cur.close()
    conn.close()

    return result
