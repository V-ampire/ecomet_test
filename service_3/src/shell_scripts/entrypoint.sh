#!/bin/sh

# Wait for clickhouse start
echo "Waiting for clickhouse..."

while ! nc -z $CLICKHOUSE_HOST $CLICKHOUSE_PORT; do
  sleep 1
done

echo "Clickhouse started"

python main.py run