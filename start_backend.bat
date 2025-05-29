@echo off
echo Starting Smart Irrigation System Backend...
cd backend
python -m pip install -r requirements.txt
python manage.py runserver
