'''
Speed Test Data Analysis
Author: Ben Lacey
Date: Jan 2024

This script performs the following:

- Loads and processes data from a CSV file.
- Aggregates performance data daily for each site.
- Compares the latest performance data with the baseline.
- Visualises the changes in load times and daily trends.
-Saves the visualisations to the charts directory.
- Saves aggregated changes to a CSV file.
- Prints a preview of both comparison and daily aggregated dataframes.
'''

import pandas as pd
import matplotlib.pyplot as plt
import os
from datetime import datetime


# Function to create directory if it doesn't exist
def create_directory(path):
    if not os.path.exists(path):
        os.makedirs(path)


# Create Charts Directory
DATA_DIRECTORY_PATH = '../../../data/'
CHARTS_DIRECTORY_PATH = '../../../data/charts'

create_directory(DATA_DIRECTORY_PATH)
create_directory(CHARTS_DIRECTORY_PATH)


# Load the CSV data
df = pd.read_csv(DATA_DIRECTORY_PATH + '/performance.csv')


# Convert Timestamp to datetime and extract the date
df['Timestamp'] = pd.to_datetime(df['Timestamp'])
df['Timestamp'] = df['Timestamp'].dt.date


# Aggregate data by Site URL and Date
daily_aggregate = df.groupby(['Site URL', 'Timestamp']).agg(
    Min_Load_Time=pd.NamedAgg(column='Load Time', aggfunc='min'),
    Max_Load_Time=pd.NamedAgg(column='Load Time', aggfunc='max'),
    Avg_Load_Time=pd.NamedAgg(column='Load Time', aggfunc='mean'),
    Std_Load_Time=pd.NamedAgg(column='Load Time', aggfunc='std')
).reset_index()


# Filter out the baseline and the latest data
baseline_df = df[df['Note'] == 'Baseline']
latest_df = df[df['Timestamp'] == df['Timestamp'].max()]

# Merge the two datasets for comparison
comparison_df = pd.merge(baseline_df, latest_df, on=['Site URL', 'Page Name'], suffixes=('_baseline', '_latest'))

# Calculate the change in load time
comparison_df['Load Time Change'] = comparison_df['Load Time_latest'] - comparison_df['Load Time_baseline']


# Aggregate changes by Site URL
aggregate_changes = comparison_df.groupby('Site URL')['Load Time Change'].agg(['mean', 'min', 'max', 'std']).reset_index()


# Visualise Load Time Changes For All Sites
for site in aggregate_changes['Site URL'].unique():
    site_data = comparison_df[comparison_df['Site URL'] == site]
    plt.figure(figsize=(10, 6))
    plt.bar(site_data['Page Name'], site_data['Load Time Change'], color='skyblue')
    plt.xlabel('Page Name')
    plt.ylabel('Load Time Change (seconds)')
    plt.title(f'Load Time Change for {site}')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()

    chart_name = f"{datetime.now().strftime('%Y%m%d')}_{site.replace('https://', '').replace('/', '_')}_load_time_change.jpg"
    plt.savefig(CHARTS_DIRECTORY_PATH + f'/load_time_change/{chart_name}')
    plt.close()


# Visualise Daily Aggregates For All Sites
for site in daily_aggregate['Site URL'].unique():
    site_data = daily_aggregate[daily_aggregate['Site URL'] == site]

    plt.figure(figsize=(12, 6))
    plt.plot(site_data['Timestamp'], site_data['Avg_Load_Time'], marker='o', label='Average Load Time')
    plt.fill_between(site_data['Timestamp'], site_data['Min_Load_Time'], site_data['Max_Load_Time'], alpha=0.1)
    plt.xlabel('Date')
    plt.ylabel('Load Time (seconds)')
    plt.title(f'Daily Load Time for {site}')
    plt.xticks(rotation=45)
    plt.legend()
    plt.tight_layout()

    chart_name = f"{datetime.now().strftime('%Y%m%d')}_{site.replace('https://', '').replace('/', '_')}_daily_load_time.jpg"

    plt.savefig(CHARTS_DIRECTORY_PATH + f'/daily_load/{chart_name}')
    plt.close()


# Save aggregated changes to a CSV file
aggregate_changes.to_csv('data/aggregate_changes.csv', index=False)


# Display the first few rows of the comparison dataframe
print(comparison_df.head())


# Display the daily aggregate data
print(daily_aggregate.head())
