# jour_479t
Repository for JOUR479T at the University of Maryland, College Park

## Slack Bot

The Slack bot in `week10/idkman.py` automatically notifies writers about their ongoing stories.

### Setup
- Install dependencies: `pip install -r requirements.txt`
- Set up environment variables in `.env`:
  - `SLACK_BOT_TOKEN`: Your Slack bot token

### Running Manually
```bash
./run_bot.sh
```

### Automated Scheduling
The bot runs continuously and automatically sends notifications every Monday at 10:25 PM using Python's `schedule` library.

To run the scheduler:
```bash
python scheduler_launcher.py start
```

To check status:
```bash
python scheduler_launcher.py status
```

To stop the scheduler:
```bash
python scheduler_launcher.py stop
```

To change the schedule, edit the `schedule.every().monday.at("22:25")` line in `week10/idkman.py`:
- `"22:25"` = 10:25 PM (24-hour format)
- Change to desired time, e.g., `"14:30"` for 2:30 PM
- For different days: `.tuesday`, `.wednesday`, etc.
