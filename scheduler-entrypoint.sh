#!/bin/sh
echo "Waiting for Database..."

while ! nc -z database 5432; do
  sleep 0.1
done

echo "Database up and running!"

python src/scheduler.py