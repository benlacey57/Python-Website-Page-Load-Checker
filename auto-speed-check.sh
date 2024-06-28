#!/bin/bash

while true
do
    python3 ./selenium_test.py >> ./logs/cron.log 2>&1
    sleep 300  # Wait for 300 seconds (5 minutes)
done