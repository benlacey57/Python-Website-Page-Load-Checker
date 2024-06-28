#!/bin/bash

# Define the drivers directory
DRIVERS_DIR="/usr/local/bin"

# Update the package list
sudo apt-get update -y

# Install Firefox
sudo apt-get install -y firefox

# Get the latest version of geckodriver
GECKODRIVER_VERSION=$(curl -s "https://api.github.com/repos/mozilla/geckodriver/releases/latest" | grep -Po '"tag_name": "\K.*?(?=")')

# Download geckodriver
wget "https://github.com/mozilla/geckodriver/releases/download/$GECKODRIVER_VERSION/geckodriver-$GECKODRIVER_VERSION-linux64.tar.gz"

# Extract and move geckodriver
tar -xvzf geckodriver-$GECKODRIVER_VERSION-linux64.tar.gz
sudo mv geckodriver $DRIVERS_DIR
sudo chmod +x $DRIVERS_DIR/geckodriver

# Clean up the downloaded tar.gz file
# rm geckodriver-$GECKODRIVER_VERSION-linux64.tar.gz

# Update PATH if necessary
if ! [[ $PATH == *"$DRIVERS_DIR"* ]]; then
    export PATH="$PATH:$DRIVERS_DIR"
    echo 'export PATH="$PATH:/usr/local/bin"' >> ~/.bashrc
fi

echo "Firefox and geckodriver have been installed successfully."
