# AI HEATMAP
# Description: Generate a Heatmap based on frequency of conversations that you had in 202X with ChatGPT.

# How to use this scriptSteps to Use this Code:
# 1. Export your ChatGPT conversations. From your ChatGPT account, go to Settings -> Data controls -> Export
# 2. Unzip the data export to the folder 'data'
# 3. Point conversation_folder to your exported data folder
# 4. Change local_tz to your local timezone so that it gets the correct timestamp of each conversation.

# Imports
import argparse
import json
import pytz
import numpy as np
import matplotlib.dates as mdates
import matplotlib.patches as patches
import matplotlib.pyplot as plt

from datetime import datetime, timezone, timedelta
from collections import Counter

def load_data(conversation_folder: str) -> dict:
    with open(f"{conversation_folder}/conversations.json", "r") as file:
        conversations = json.load(file)
        return conversations

def get_utc_timestamp(conversations: list, local_tz: str) -> list:

    times_utc = []

    for conversation in conversations:
        unix_timestamp = conversation["create_time"]
        utc_datetime = datetime.fromtimestamp(unix_timestamp, tz=timezone.utc)

        pt_datetime = utc_datetime.astimezone(pytz.timezone(local_tz))
        times_utc.append(pt_datetime)

    return times_utc

def get_date_range(conversations: list, local_tz: str, year: int) -> list:

    times_utc = get_utc_timestamp(conversations, local_tz)

    # Create a full year date range for the calendar
    start_date = datetime(year, 1, 1).date()
    end_date = datetime(year, 12, 31).date()

    # Convert convo_times to dates and filter for the given year
    just_dates = [t.date() for t in times_utc if t.year == year]
    date_counts = Counter(just_dates)

    total_days = (end_date - start_date).days + 1
    date_range = [start_date + timedelta(days=i) for i in range(total_days)]

    return date_range, date_counts, total_days

def create_year_heatmap(conversations: list, local_tz: str, year: str):

    date_range, date_counts, total_days = get_date_range(conversations, local_tz, year)
    start_date, end_date = date_range[0], date_range[-1]

    # Prepare data for plotting
    data = []
    for date in date_range:
        week = ((date - start_date).days + start_date.weekday()) // 7
        day_of_week = date.weekday()
        count = date_counts.get(date, 0)
        data.append((week, day_of_week, count))

    weeks_in_year = (end_date - start_date).days // 7 + 1

    # Plot the heatmap
    plt.figure(figsize=(15, 8))
    ax = plt.gca()
    ax.set_aspect('equal')

    max_count_date = max(date_counts, key=date_counts.get)
    max_count = date_counts[max_count_date]
    p90_count = np.percentile(list(date_counts.values()), 90)
    for week, day_of_week, count in data:
        color = plt.cm.Greens((count + 1) / p90_count) if count > 0 else 'lightgray'
        rect = patches.Rectangle((week, day_of_week), 1, 1, linewidth=0.5, edgecolor='black', facecolor=color)
        ax.add_patch(rect)

    # Replace week numbers with month names below the heatmap
    month_starts = [start_date + timedelta(days=i) for i in range(total_days)
                    if (start_date + timedelta(days=i)).day == 1]
    for month_start in month_starts:
        week = (month_start - start_date).days // 7
        plt.text(week + 0.5, 7.75, month_start.strftime('%b'), ha='center', va='center', fontsize=10, rotation=0)

    # Adjustments for readability
    ax.set_xlim(-0.5, weeks_in_year + 0.5)
    ax.set_ylim(-0.5, 8.5)
    plt.title(
        f'{year} ChatGPT Conversation Heatmap (total={sum(date_counts.values())}).\nMost active day: {max_count_date} with {max_count} convos.',
        fontsize=16
    )
    plt.xticks([])
    plt.yticks(range(7), ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'])
    plt.gca().invert_yaxis()
    plt.show()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Script to process ChatGPT exported data.")
    parser.add_argument("--chatgpt_data_folder", type=str, required=True, help="Path to the ChatGPT exported data folder.")
    parser.add_argument("--local_tz", type=str, required=True, help="Local timezone.")
    parser.add_argument("--year", type=str, required=True, help="Year filter for data analysis.")

    args = parser.parse_args()

    conversations = load_data(args.chatgpt_data_folder)
    create_year_heatmap(conversations, args.local_tz, int(args.year))
