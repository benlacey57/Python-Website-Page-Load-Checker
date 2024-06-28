#!/bin/bash

# This script automatically commits and pushes changes to the repository every 60 minutes

# Other time options:
# sleep 1800   # Sleep for 30 minutes
# sleep 900    # Sleep for 15 minutes

while true; do
    git add .
    git commit -m "Auto-Commit Speed Test Data"
    git push
    sleep 3600   # Sleep for 60 minutes
done
