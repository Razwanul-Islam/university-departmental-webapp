import os
import subprocess
import sys
from pathlib import Path

root = Path(__file__).resolve().parents[2]
os.environ["SQLITE_PATH"] = str(root / ".browser-test.sqlite3")
os.environ["DJANGO_DEBUG"] = "true"
commands = [
    ["manage.py", "migrate", "--noinput"],
    ["seed.py"],
    ["manage.py", "runserver", "127.0.0.1:8000", "--noreload"],
]
for command in commands:
    subprocess.run([sys.executable, *command], cwd=root, check=True)
