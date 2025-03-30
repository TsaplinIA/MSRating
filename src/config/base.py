from pathlib import Path

PROJECT_DIR = Path(__file__).parent.parent.parent
TEMPLATE_DIR = PROJECT_DIR / "templates"
STATIC_DIR = PROJECT_DIR / "static"

APP_SECRET_KEY = 'change'
SQLALCHEMY_DATABASE_URI = 'change'
ADMIN_SECRET_CODE = 'change'

HOST = '0.0.0.0'
PORT = 8080

LOG_LEVEL = 'INFO'
