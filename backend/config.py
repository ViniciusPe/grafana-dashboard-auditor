import os
from dotenv import load_dotenv

load_dotenv()

GRAFANA_URL = os.getenv("GRAFANA_URL")
GRAFANA_TOKEN = os.getenv("GRAFANA_TOKEN")

DB_HOST = os.getenv("DB_HOST", "postgres")
DB_NAME = os.getenv("DB_NAME", "grafana")
DB_USER = os.getenv("DB_USER", "grafana")
DB_PASSWORD = os.getenv("DB_PASSWORD", "grafana")
DB_PORT = int(os.getenv("DB_PORT", "5432"))
