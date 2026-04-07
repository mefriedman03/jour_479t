
#!/workspaces/jour_479t/venv/bin/python
# Note: This script is configured to use the virtual environment Python directly.
# Make sure the venv is set up at /workspaces/jour_479t/venv
# To run: ./week10/idkman.py (after making it executable with chmod +x week10/idkman.py)

import argparse
import os
import time
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from slack_sdk import WebClient
import schedule

# Set time zone to Eastern Time
os.environ['TZ'] = 'America/New_York'
time.tzset()

# Load environment variables from .env file
load_dotenv(Path(__file__).resolve().parents[1] / ".env")

SLACK_TOKEN = os.environ.get("SLACK_BOT_TOKEN")
if not SLACK_TOKEN:
    raise ValueError("SLACK_BOT_TOKEN environment variable not set. Please add it to .env or set it in your shell.")

CHANNEL = os.environ.get("SLACK_CHANNEL", "#jour479t")
SCHEDULE_TIME = os.environ.get("SCHEDULE_TIME", "22:50")

# Convert to CSV export format
SHEET_URL = "https://docs.google.com/spreadsheets/d/12djudSEQIbyRSfEq6NsYbTJB8bvXfBb0d8Ly6xnEO-A/export?format=csv"

client = WebClient(token=SLACK_TOKEN)

def get_ongoing_stories():
    try:
        print("Fetching spreadsheet data...")
        df = pd.read_csv(SHEET_URL)
        if "status" not in df.columns:
            raise KeyError(f"'status' column not found. Available columns: {df.columns.tolist()}")
        if "writer_name" not in df.columns:
            raise KeyError(f"'writer_name' column not found. Available columns: {df.columns.tolist()}")
        if "slug" not in df.columns:
            raise KeyError(f"'slug' column not found. Available columns: {df.columns.tolist()}")
        if "user_id" not in df.columns:
            raise KeyError(f"'user_id' column not found. Available columns: {df.columns.tolist()}")
        ongoing = df[df["status"] == "ongoing"]
        print(f"Found {len(ongoing)} ongoing stories.")
        return ongoing
    except Exception as e:
        print(f"Error fetching spreadsheet: {e}")
        raise

def group_by_writer(df):
    grouped = {}
    for _, row in df.iterrows():
        user_id = row["user_id"]
        writer = row["writer_name"]
        slug = row["slug"]

        # Skip if user_id is missing or empty
        if pd.isna(user_id) or str(user_id).strip() == "":
            print(f"Skipping story '{slug}' for writer '{writer}' due to missing user_id.")
            continue

        if user_id not in grouped:
            grouped[user_id] = {"writer": writer, "stories": []}
        grouped[user_id]["stories"].append(slug)

    return grouped

def send_messages(grouped, channel=CHANNEL):
    for user_id, data in grouped.items():
        writer = data["writer"]
        stories = data["stories"]
        story_list = "\n• " + "\n• ".join(stories)

        message = (
            f"Hi <@{user_id}>. You have stories in the ongoing section:{story_list}\n\n"
            "Please provide updates."
        )

        try:
            response = client.chat_postMessage(
                channel=channel,
                text=message
            )
            print(f"Message sent to {writer} (user_id: {user_id}) in {channel} successfully.")
        except Exception as e:
            print(f"Error sending message to {writer} (user_id: {user_id}): {e}")


def run_bot(channel=None):
    """Function to run the bot once - used for scheduling"""
    channel = channel or CHANNEL
    print("Starting Slack bot...")
    try:
        df = get_ongoing_stories()
        grouped = group_by_writer(df)
        print(f"Grouped stories by {len(grouped)} users.")
        send_messages(grouped, channel=channel)
        print("Finished sending messages.")
    except Exception as e:
        print(f"Error running bot: {e}")


def parse_args():
    parser = argparse.ArgumentParser(description="Run the Slack bot scheduler or send messages immediately.")
    parser.add_argument("--once", action="store_true", help="Run the bot once immediately and exit.")
    parser.add_argument("--channel", default=None, help="Override the Slack channel to send messages to.")
    return parser.parse_args()


def main():
    args = parse_args()
    if args.channel:
        print(f"Using override channel: {args.channel}")

    if args.once:
        print("Running bot once immediately.")
        run_bot(channel=args.channel)
        return

    schedule_time = SCHEDULE_TIME
    print(f"Slack bot scheduler started. Will run every Monday at {schedule_time} ET.")
    print("Press Ctrl+C to stop.")

    schedule.every().monday.at(schedule_time).do(lambda: run_bot(channel=args.channel))

    print("Scheduler is running...")

    # Run the scheduler continuously
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    except KeyboardInterrupt:
        print("\nScheduler stopped by user.")
    except Exception as e:
        print(f"Scheduler error: {e}")
        raise

if __name__ == "__main__":
    main()