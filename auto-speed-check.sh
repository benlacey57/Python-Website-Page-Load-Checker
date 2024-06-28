#!/bin/bash

# This script runs the main Python script and logs the output every 5 minutes

# Other time options:
# sleep 3600   # Wait 60 minutes
# sleep 1800   # Wait 30 minutes
# sleep 900    # Wait 15 minutes

while true
do
    python3 ./main.py >> ./logs/cron.log 2>&1
    sleep 300  # Wait 5 minutes
done