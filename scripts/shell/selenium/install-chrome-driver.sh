#!/bin/bash

# Define the drivers directory
DRIVERS_DIR="/usr/local/bin"

# Update the package list
sudo apt-get update -y

# Install dependencies for Google Chrome
sudo apt-get install -y wget gnupg2 software-properties-common

# Download and install Google Chrome
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo dpkg -i google-chrome-stable_current_amd64.deb
sudo apt-get install -y -f  # Fix any installation errors

# Remove the downloaded Chrome .deb file
rm google-chrome-stable_current_amd64.deb

# Get the version of the installed Chrome
CHROME_VERSION=$(google-chrome --version | cut -f 3 -d ' ' | cut -d '.' -f 1)

# Determine the matching version of ChromeDriver
DRIVER_VERSION=$(wget -qO- "https://chromedriver.storage.googleapis.com/LATEST_RELEASE_$CHROME_VERSION")

# Download ChromeDriver
wget "https://chromedriver.storage.googleapis.com/$DRIVER_VERSION/chromedriver_linux64.zip"

# Extract and move ChromeDriver
unzip chromedriver_linux64.zip
sudo mv chromedriver $DRIVERS_DIR
sudo chmod +x $DRIVERS_DIR/chromedriver

# Clean up the downloaded zip file
rm chromedriver_linux64.zip

# Update PATH if necessary
if ! [[ $PATH == *"$DRIVERS_DIR"* ]]; then
    export PATH="$PATH:$DRIVERS_DIR"
    echo 'export PATH="$PATH:/usr/local/bin"' >> ~/.bashrc
fi

echo "Google Chrome and ChromeDriver have been installed successfully."
