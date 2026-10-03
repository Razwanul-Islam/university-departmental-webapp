import os
import subprocess
import sys
from pathlib import Path

root = Path(__file__).resolve().parents[2]
os.environ['SQLITE_PATH'] = str(root / '.browser-test.sqlite3')
os.environ['DJANGO_DEBUG'] = 'true'
for args in [('migrate', '--noinput'), ('seed_demo',), ('runserver', '127.0.0.1:8000', '--noreload')]:
    subprocess.run([sys.executable, str(root / 'manage.py'), *args], cwd=root, check=True)
