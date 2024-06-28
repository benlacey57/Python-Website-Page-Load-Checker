"""
Speed Test Data Analysis

Author: Ben Lacey
Date: Jun 2024

This script performs the following:
- Loads and processes data from a CSV file.
- Aggregates performance data daily for each site.
- Compares the latest performance data with the baseline.
- Visualizes the changes in load times and daily trends.
- Saves the visualizations to the charts directory.
- Saves aggregated changes to a CSV file.
- Prints a preview of both comparison and daily aggregated dataframes.
"""

import pandas as pd
import matplotlib.pyplot as plt
import os
from pathlib import Path
from datetime import datetime

# Function to create directory if it doesn't exist
def create_directory(path):
    if not os.path.exists(path):
        os.makedirs(path)
        print(f"Created directory: {path}")

# Get the project root directory
project_root = Path(__file__).resolve().parents[2]  # Adjust as necessary
data_directory_path = project_root / 'data'

# Prompt the user for the CSV file to analyze
csv_file_name = input("Enter the filename of the CSV file to analyze (within data/): ")
csv_file_path = data_directory_path / csv_file_name

# Check if the file exists
if not csv_file_path.exists():
    print(f"Error: The file {csv_file_path} does not exist.")
    exit(1)

# Load the CSV data
df = pd.read_csv(csv_file_path)

# Display target page load time config
target_load_time = df['Target Load Time'].iloc[0] if 'Target Load Time' in df.columns else None
if target_load_time:
    print(f"Target Page Load Time: {target_load_time} seconds")

# List the pages and show the page level config options
print("\nPages and Config Options:\n")
pages = df['Page Name'].unique()
for page in pages:
    page_config = df[df['Page Name'] == page].iloc[0]
    print(f"Page: {page}")
    print(f"  URL: {page_config['Page URL']}")
    if 'Config Options' in page_config:
        print(f"  Config Options: {page_config['Config Options']}")
    print("")

# Convert Timestamp to datetime and extract the date
df['Timestamp'] = pd.to_datetime(df['Timestamp'])
df['Date'] = df['Timestamp'].dt.date

# Create necessary directories based on the site URL
site_keys = df['Site URL'].unique()
for site in site_keys:
    site_key = site.replace('https://', '').replace('/', '_')
    site_analysis_directory_path = data_directory_path / site_key / 'analysis'
    create_directory(site_analysis_directory_path)

    charts_directory_path = data_directory_path / site_key / 'charts'
    create_directory(charts_directory_path)
    
    load_time_change_directory_path = charts_directory_path / 'load_time_change'
    create_directory(load_time_change_directory_path)
    
    daily_load_directory_path = charts_directory_path / 'daily_load'
    create_directory(daily_load_directory_path)
    
    page_breakdown_directory_path = charts_directory_path / 'page_breakdown'
    create_directory(page_breakdown_directory_path)

# Aggregate data by Site URL and Date
daily_aggregate = df.groupby(['Site URL', 'Date']).agg(
    Min_Load_Time=pd.NamedAgg(column='Load Time', aggfunc='min'),
    Max_Load_Time=pd.NamedAgg(column='Load Time', aggfunc='max'),
    Avg_Load_Time=pd.NamedAgg(column='Load Time', aggfunc='mean'),
    Std_Load_Time=pd.NamedAgg(column='Load Time', aggfunc='std')
).reset_index()

# Filter out the baseline and the latest data
baseline_df = df[df['Note'] == 'Baseline']
latest_df = df[df['Date'] == df['Date'].max()]

# Merge the two datasets for comparison
comparison_df = pd.merge(baseline_df, latest_df, on=['Site URL', 'Page Name'], suffixes=('_baseline', '_latest'))
comparison_df['Load Time Change'] = comparison_df['Load Time_latest'] - comparison_df['Load Time_baseline']

# Aggregate changes by Site URL
aggregate_changes = comparison_df.groupby('Site URL')['Load Time Change'].agg(['mean', 'min', 'max', 'std']).reset_index()

# Visualize Load Time Changes For All Sites
for site in aggregate_changes['Site URL'].unique():
    site_data = comparison_df[comparison_df['Site URL'] == site]
    plt.figure(figsize=(10, 6))
    plt.bar(site_data['Page Name'], site_data['Load Time Change'], color='skyblue')
    plt.xlabel('Page Name')
    plt.ylabel('Load Time Change (seconds)')
    plt.title(f'Load Time Change for {site}')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    
    site_key = site.replace('https://', '').replace('/', '_')
    chart_name = "load_time_change.jpg"
    plt.savefig(load_time_change_directory_path / chart_name)
    plt.close()
    print(f"Saved load time change chart for {site}.")

# Visualize Daily Aggregates For All Sites
for site in daily_aggregate['Site URL'].unique():
    site_data = daily_aggregate[daily_aggregate['Site URL'] == site]
    
    plt.figure(figsize=(12, 6))
    plt.plot(site_data['Date'], site_data['Avg_Load_Time'], marker='o', label='Average Load Time')
    plt.fill_between(site_data['Date'], site_data['Min_Load_Time'], site_data['Max_Load_Time'], alpha=0.1)
    plt.xlabel('Date')
    plt.ylabel('Load Time (seconds)')
    plt.title(f'Daily Load Time for {site}')
    plt.xticks(rotation=45)
    plt.legend()
    plt.tight_layout()
    
    site_key = site.replace('https://', '').replace('/', '_')
    chart_name = "daily_load_time.jpg"
    plt.savefig(daily_load_directory_path / chart_name)
    plt.close()
    print(f"Saved daily load time chart for {site}.")

# Create a page breakdown over time
for site in df['Site URL'].unique():
    site_data = df[df['Site URL'] == site]
    
    for page in site_data['Page Name'].unique():
        page_data = site_data[site_data['Page Name'] == page]
        
        plt.figure(figsize=(12, 6))
        plt.plot(page_data['Date'], page_data['Load Time'], marker='o', label='Load Time')
        plt.xlabel('Date')
        plt.ylabel('Load Time (seconds)')
        plt.title(f'Load Time Over Time for {site} - {page}')
        plt.xticks(rotation=45)
        plt.legend()
        plt.tight_layout()
        
        site_key = site.replace('https://', '').replace('/', '_')
        chart_name = f"{page.replace('/', '_')}_page_breakdown.jpg"
        plt.savefig(page_breakdown_directory_path / chart_name)
        plt.close()
        print(f"Saved page breakdown chart for {site} - {page}.")

# Additional analysis and charts
# 1. Boxplot of Load Times
for site in df['Site URL'].unique():
    site_data = df[df['Site URL'] == site]
    plt.figure(figsize=(10, 6))
    site_data.boxplot(column='Load Time', by='Page Name')
    plt.title(f'Boxplot of Load Times for {site}')
    plt.suptitle('')
    plt.xlabel('Page Name')
    plt.ylabel('Load Time (seconds)')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    
    site_key = site.replace('https://', '').replace('/', '_')
    chart_name = "boxplot_load_times.jpg"
    plt.savefig(charts_directory_path / chart_name)
    plt.close()
    print(f"Saved boxplot of load times for {site}.")

# 2. Histogram of Load Times
for site in df['Site URL'].unique():
    site_data = df[df['Site URL'] == site]
    plt.figure(figsize=(10, 6))
    site_data['Load Time'].hist(bins=20)
    plt.title(f'Histogram of Load Times for {site}')
    plt.xlabel('Load Time (seconds)')
    plt.ylabel('Frequency')
    plt.tight_layout()
    
    site_key = site.replace('https://', '').replace('/', '_')
    chart_name = "histogram_load_times.jpg"
    plt.savefig(charts_directory_path / chart_name)
    plt.close()
    print(f"Saved histogram of load times for {site}.")

# 3. Scatter Plot of Load Time vs Number of Requests
for site in df['Site URL'].unique():
    site_data = df[df['Site URL'] == site]
    plt.figure(figsize=(10, 6))
    plt.scatter(site_data['Number Requests'], site_data['Load Time'])
    plt.title(f'Scatter Plot of Load Time vs Number of Requests for {site}')
    plt.xlabel('Number of Requests')
    plt.ylabel('Load Time (seconds)')
    plt.tight_layout()
    
    site_key = site.replace('https://', '').replace('/', '_')
    chart_name = "scatter_requests_vs_load_time.jpg"
    plt.savefig(charts_directory_path / chart_name)
    plt.close()
    print(f"Saved scatter plot of load time vs number of requests for {site}.")

# 4. Line Plot of Number of Requests Over Time
for site in df['Site URL'].unique():
    site_data = df[df['Site URL'] == site]
    plt.figure(figsize=(12, 6))
    plt.plot(site_data['Date'], site_data['Number Requests'], marker='o')
    plt.title(f'Number of Requests Over Time for {site}')
    plt.xlabel('Date')
    plt.ylabel('Number of Requests')
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    site_key = site.replace('https://', '').replace('/', '_')
    chart_name = "line_requests_over_time.jpg"
    plt.savefig(charts_directory_path / chart_name)
    plt.close()
    print(f"Saved line plot of number of requests over time for {site}.")

# 5. Heatmap of Load Times by Page and Date
for site in df['Site URL'].unique():
    site_data = df[df['Site URL'] == site]
    pivot_table = site_data.pivot("Date", "Page Name", "Load Time")
    plt.figure(figsize=(12, 6))
    sns.heatmap(pivot_table, annot=True, fmt=".1f", cmap="YlGnBu")
    plt.title(f'Heatmap of Load Times for {site}')
    plt.xlabel('Page Name')
    plt.ylabel('Date')
    plt.tight_layout()
    
    site_key = site.replace('https://', '').replace('/', '_')
    chart_name = "heatmap_load_times.jpg"
    plt.savefig(charts_directory_path / chart_name)
    plt.close()
    print(f"Saved heatmap of load times for {site}.")

# Save aggregated changes to a CSV file
for site in aggregate_changes['Site URL'].unique():
    site_key = site.replace('https://', '').replace('/', '_')
    aggregate_changes_path = data_directory_path / site_key / 'analysis' / 'aggregate_changes.csv'
    site_aggregate_changes = aggregate_changes[aggregate_changes['Site URL'] == site]
    site_aggregate_changes.to_csv(aggregate_changes_path, index=False)
    print(f"Saved aggregate changes to {aggregate_changes_path}.")

# Save comparison dataframe to CSV
for site in comparison_df['Site URL'].unique():
    site_key = site.replace('https://', '').replace('/', '_')
    comparison_path = data_directory_path / site_key / 'analysis' / 'comparison.csv'
    site_comparison_df = comparison_df[comparison_df['Site URL'] == site]
    site_comparison_df.to_csv(comparison_path, index=False)
    print(f"Saved comparison dataframe to {comparison_path}.")

# Save daily aggregate dataframe to CSV
for site in daily_aggregate['Site URL'].unique():
    site_key = site.replace('https://', '').replace('/', '_')
    daily_aggregate_path = data_directory_path / site_key / 'analysis' / 'daily_aggregate.csv'
    site_daily_aggregate = daily_aggregate[daily_aggregate['Site URL'] == site]
    site_daily_aggregate.to_csv(daily_aggregate_path, index=False)
    print(f"Saved daily aggregate dataframe to {daily_aggregate_path}.")

# Aggregate load time stats by site
load_time_stats = df.groupby('Site URL').agg(
    Min_Load_Time=pd.NamedAgg(column='Load Time', aggfunc='min'),
    Max_Load_Time=pd.NamedAgg(column='Load Time', aggfunc='max'),
    Avg_Load_Time=pd.NamedAgg(column='Load Time', aggfunc='mean'),
    Std_Load_Time=pd.NamedAgg(column='Load Time', aggfunc='std')
).reset_index()

# Save load time stats to a CSV file
for site in load_time_stats['Site URL'].unique():
    site_key = site.replace('https://', '').replace('/', '_')
    load_time_stats_path = data_directory_path / site_key / 'analysis' / 'load_time_stats.csv'
    site_load_time_stats = load_time_stats[load_time_stats['Site URL'] == site]
    site_load_time_stats.to_csv(load_time_stats_path, index=False)
    print(f"Saved load time stats to {load_time_stats_path}.")

# Display the first few rows of the comparison dataframe
print("\n\nComparison DataFrame:\n")
print(comparison_df.head())

# Display the daily aggregate data
print("\n\nDaily Aggregate DataFrame:\n")
print(daily_aggregate.head())

# Display the load time stats
print("\n\nLoad Time Stats DataFrame:\n")
print(load_time_stats.head())
print("\n\nData Analysis Complete!\n\n")
