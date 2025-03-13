from pathlib import Path

PROJECT_DIR = Path(__file__).parent.parent.parent
TEMPLATE_DIR = PROJECT_DIR / "templates"
STATIC_DIR = PROJECT_DIR / "static"

APP_SECRET_KEY = 'change'
SQLALCHEMY_DATABASE_URI = 'change'
ADMIN_SECRET_CODE = 'change'

HOST = '0.0.0.0'
PORT = 8080

# Уровень логирования
# Один из DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_LEVEL = 'INFO'

SEASONS = {
    '2025-1': ('2025-01-01', '2025-02-28'),
    '2025-2': ('2025-03-01', '2025-04-30'),
    '2025-3': ('2025-05-01', '2025-06-30'),
    '2025-4': ('2025-07-01', '2025-08-31'),
    '2025-5': ('2025-09-01', '2025-10-31'),
    '2025-6': ('2025-11-01', '2025-12-31'),
}

FIXED_PERIODS = [
    {'value': 'all', 'name': 'Все время'},
    {'value': '2025-1', 'name': 'Январь-Февраль 2025'},
    {'value': '2025-2', 'name': 'Март-Апрель 2025'},
    {'value': '2025-3', 'name': 'Май-Июнь 2025'},
    {'value': '2025-4', 'name': 'Июль-Август 2025'},
    {'value': '2025-5', 'name': 'Сентябрь-Октябрь 2025'},
    {'value': '2025-6', 'name': 'Ноябрь-Декабрь 2025'}
]
