# Slack Bot - Story Notification System

Automated Slack bot that notifies writers about their ongoing stories by fetching data from a Google Sheets spreadsheet.

## Installation & Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up environment variables** in a `.env` file in the project root:
   ```env
   SLACK_BOT_TOKEN=xoxb-your-token-here
   SLACK_CHANNEL=#jour479t
   SCHEDULE_TIME=22:50
   SHEET_URL=https://docs.google.com/spreadsheets/d/12djudSEQIbyRSfEq6NsYbTJB8bvXfBb0d8Ly6xnEO-A/export?format=csv
   ```

   Required variables:
   - `SLACK_BOT_TOKEN`: Your Slack bot token (required) - Keep this secret, do not commit to Git
   - `SLACK_CHANNEL`: Target channel (default: `#jour479t`)
   - `SCHEDULE_TIME`: Time to send notifications in 24-hour format (default: `22:50`)
   - `SHEET_URL`: Google Sheets CSV export link (default: The jour479t stories spreadsheet)

## Running Manually

Send notifications immediately without scheduling:
```bash
python week10/idkman.py --once
```

Override the channel:
```bash
python week10/idkman.py --once --channel "#general"
```

## Automated Scheduling

The bot runs as a daemon and automatically sends notifications every Monday at the time specified in `SCHEDULE_TIME`.

**Start the scheduler:**
```bash
python scheduler_launcher.py start
```

**Check scheduler status:**
```bash
python scheduler_launcher.py status
```

**Stop the scheduler:**
```bash
python scheduler_launcher.py stop
```

## Monitoring & Troubleshooting

The daemon logs all output and errors to:
```bash
tail -f /tmp/slack_bot_scheduler.log
```

Check if the scheduler is running:
```bash
ps aux | grep idkman.py
```

## Configuration

**Change notification time:**
Set `SCHEDULE_TIME` in `.env` to a 24-hour format time:
- `"22:50"` = 10:50 PM
- `"14:30"` = 2:30 PM
- `"09:00"` = 9:00 AM

The bot currently runs every Monday. To modify the schedule, edit the `schedule` line in `week10/idkman.py`:
```python
schedule.every().monday.at(schedule_time).do(...)
```

Supported days: `.monday`, `.tuesday`, `.wednesday`, `.thursday`, `.friday`, `.saturday`, `.sunday`

## How It Works

1. Fetches spreadsheet data from Google Sheets (must have columns: `status`, `writer_name`, `slug`, `user_id`)
2. Filters for "ongoing" stories
3. Groups stories by writer
4. Sends personalized Slack messages to each writer with their ongoing stories
5. Logs all actions and errors

## Error Handling

The bot includes robust error handling:
- Missing columns in the spreadsheet are clearly reported
- Missing `user_id` values are skipped with logging
- Network errors are caught and logged without crashing the scheduler
- All errors are written to `/tmp/slack_bot_scheduler.log`

## Project Files

- **idkman.py** - Main bot logic with scheduling and message sending
- **slackbot.py** - Simple example of sending a basic Slack message
- **slackbot_instructions.md** - Additional instructions and notes
- **assets/** - Storage for any additional files/resources
