#!/bin/bash

while true; do
    git add .
    git commit -m "Auto-Commit Speed Test Data"
    git psh
    sleep 3600   # Sleep for 60 minutes
done
