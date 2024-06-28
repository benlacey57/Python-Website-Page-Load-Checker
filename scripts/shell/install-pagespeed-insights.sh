#!/bin/bash

# Install Node.js and npm if they are not installed
which node > /dev/null || {
  echo "Installing Node.js..."
  curl -sL https://deb.nodesource.com/setup_14.x | sudo -E bash -
  sudo apt-get install -y nodejs
}

# Install PageSpeed Insights
echo "Installing PageSpeed Insights..."
sudo npm install -g psi

# Open Google API Console for setting up credentials
echo "Please open the following URL in your web browser to set up Google API credentials:"
echo "https://console.developers.google.com/"
echo "Create a new project, enable the PageSpeed Insights API, and create an API key."
