'''
Run Page Speed Insights
Author: Ben Lacey
Date: Jan 2024

- This script runs PageSpeed Insights for each page specified in your config.json file.
- The results, including the timestamp, site URL, page URL, and selected metrics, are saved in a Pandas DataFrame.
- The DataFrame is then saved as a CSV file to data/page-speed-insights.csv.
'''

import json
import os
import pandas as pd
import googleapiclient.discovery
from datetime import datetime

# Function to create directory if it doesn't exist
def create_directory(path):
    if not os.path.exists(path):
        os.makedirs(path)

# Load configuration from config.json
with open('../../../config.json', 'r') as file:
    config = json.load(file)

# Set up the PageSpeed Insights service
service = googleapiclient.discovery.build('pagespeedonline', 'v5')

# Prepare data for the DataFrame
data = []

for site in config['sites']:
    for page in config['pages']:
        page_url = site['url'] + page['url']
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        for strategy in ['desktop', 'mobile']:
            result = service.pagespeedapi().runpagespeed(url=page_url, strategy=strategy).execute()

            # Extracting the desired metrics
            audits = result.get('lighthouseResult', {}).get('audits', {})
            diagnostics = audits.get('diagnostics', {}).get('details', {}).get('items', [{}])[0]

            data.append({
                'Timestamp': timestamp,
                'Site URL': site['url'],
                'Page URL': page_url,
                'Strategy': strategy,
                'Performance Score': result.get('lighthouseResult', {}).get('categories', {}).get('performance', {}).get('score'),
                'First Contentful Paint': audits.get('first-contentful-paint', {}).get('displayValue'),
                'Speed Index': audits.get('speed-index', {}).get('displayValue'),
                'Largest Contentful Paint': audits.get('largest-contentful-paint', {}).get('displayValue'),
                'Time to Interactive': audits.get('interactive', {}).get('displayValue'),
                'Total Blocking Time': audits.get('total-blocking-time', {}).get('displayValue'),
                'Cumulative Layout Shift': audits.get('cumulative-layout-shift', {}).get('displayValue'),
                # Additional diagnostics metrics
                'Main Thread Work Breakdown': diagnostics.get('mainThreadWorkBreakdown', []),
                'Bootup Time': diagnostics.get('bootupTime', 0),
                'Network Requests': diagnostics.get('numRequests', 0),
                'Total Byte Weight': diagnostics.get('totalByteWeight', 0)
                # You can add more metrics as needed
            })

# Create DataFrame and save to CSV
df = pd.DataFrame(data)
create_directory('data')
df.to_csv('../../../data/page-speed-insights.csv', index=False)

print('PageSpeed Insights data saved to CSV successfully.')
