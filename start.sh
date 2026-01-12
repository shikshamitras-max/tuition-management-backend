#!/usr/bin/env bash
echo "Initializing database..."

python init_db.py
python init_exam_db.py
python init_institute.py
python setup_institute.py

echo "Starting server..."
gunicorn app:app