#!/bin/sh
echo "Waiting for Database..."

while ! nc -z database 5432; do
  sleep 0.1
done

echo "Database up and running!"

gunicorn --bind 0.0.0.0:5001 -w 4 --pythonpath src src.app:app