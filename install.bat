@echo off

REM Step 1: Install Python dependencies
pip install -r requirements.txt

REM Step 2: Run Django migrations
python manage.py migrate

REM Step 3: Run Django local server
start "" python manage.py runserver

REM Step 4: Open Chrome with the local server URL
start chrome http://127.0.0.1:8000
