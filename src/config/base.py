from pathlib import Path

PROJECT_DIR = Path(__file__).parent.parent.parent

APP_SECRET_KEY = 'change'
SQLALCHEMY_DATABASE_URI = 'change'
ADMIN_SECRET_CODE = 'change'

HOST = '0.0.0.0'
PORT = 8080

# Уровень логирования
# Один из DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_LEVEL = 'INFO'

if __name__ == '__main__':
    ...
