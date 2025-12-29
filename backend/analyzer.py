from grafana_api import list_dashboards, get_dashboard


def extract_panels(panels):
    all_panels = []

    for panel in panels:
        # painel normal
        if panel.get("type") != "row":
            all_panels.append(panel)

        # painéis dentro de rows ou panels aninhados
        if "panels" in panel:
            all_panels.extend(extract_panels(panel["panels"]))

    return all_panels


def find_broken_dashboards():
    broken = []

    dashboards = list_dashboards()

    for d in dashboards:
        uid = d["uid"]
        title = d["title"]

        try:
            dash = get_dashboard(uid)
            dashboard = dash["dashboard"]

            panels = extract_panels(dashboard.get("panels", []))

            if not panels:
                broken.append({
                    "uid": uid,
                    "title": title,
                    "reason": "Dashboard without panels"
                })
                continue

            for panel in panels:
                datasource = panel.get("datasource")

                if not datasource:
                    broken.append({
                        "uid": uid,
                        "title": title,
                        "reason": "Panel without datasource"
                    })
                    break

                targets = panel.get("targets", [])
                if not targets:
                    broken.append({
                        "uid": uid,
                        "title": title,
                        "reason": "Panel without queries"
                    })
                    break

        except Exception as e:
            broken.append({
                "uid": uid,
                "title": title,
                "reason": f"Failed to load dashboard: {e}"
            })

    return broken
