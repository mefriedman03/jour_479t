#!/workspaces/jour_479t/venv/bin/python
"""
Slack Bot Scheduler Launcher
Runs the bot scheduler as a background daemon process.
"""

import os
import sys
import time
import subprocess
import signal
import atexit
from pathlib import Path

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent))

def daemonize():
    """Daemonize the process"""
    # Fork once
    try:
        pid = os.fork()
        if pid > 0:
            sys.exit(0)  # Exit parent
    except OSError as e:
        sys.stderr.write(f"Fork #1 failed: {e}\n")
        sys.exit(1)

    # Decouple from parent environment
    os.chdir("/")
    os.setsid()
    os.umask(0)

    # Fork twice
    try:
        pid = os.fork()
        if pid > 0:
            sys.exit(0)  # Exit second parent
    except OSError as e:
        sys.stderr.write(f"Fork #2 failed: {e}\n")
        sys.exit(1)

    # Redirect standard file descriptors
    sys.stdout.flush()
    sys.stderr.flush()
    with open('/dev/null', 'r') as f:
        os.dup2(f.fileno(), sys.stdin.fileno())
    with open('/dev/null', 'a+') as f:
        os.dup2(f.fileno(), sys.stdout.fileno())
        os.dup2(f.fileno(), sys.stderr.fileno())

def start_scheduler():
    """Start the scheduler"""
    print("Starting Slack bot scheduler...")

    # Check if already running
    try:
        with open('/tmp/slack_bot_scheduler.pid', 'r') as f:
            pid = int(f.read().strip())
        try:
            os.kill(pid, 0)  # Check if process exists
            print(f"Scheduler already running with PID {pid}")
            return
        except OSError:
            pass  # Process doesn't exist, remove stale PID file
    except FileNotFoundError:
        pass

    # Daemonize
    daemonize()

    # Write PID file
    with open('/tmp/slack_bot_scheduler.pid', 'w') as f:
        f.write(str(os.getpid()))

    # Change to project directory and activate venv
    os.chdir('/workspaces/jour_479t')
    os.environ['PATH'] = '/workspaces/jour_479t/venv/bin:' + os.environ['PATH']

    # Import and run the scheduler
    try:
        from week10.idkman import main
        main()
    except Exception as e:
        with open('/tmp/slack_bot_scheduler.log', 'a') as f:
            f.write(f"Error starting scheduler: {e}\n")
        sys.exit(1)

def stop_scheduler():
    """Stop the scheduler"""
    try:
        with open('/tmp/slack_bot_scheduler.pid', 'r') as f:
            pid = int(f.read().strip())
        os.kill(pid, signal.SIGTERM)
        print(f"Stopped scheduler with PID {pid}")
        os.remove('/tmp/slack_bot_scheduler.pid')
    except FileNotFoundError:
        print("Scheduler not running")
    except OSError as e:
        print(f"Error stopping scheduler: {e}")

def status_scheduler():
    """Check scheduler status"""
    try:
        with open('/tmp/slack_bot_scheduler.pid', 'r') as f:
            pid = int(f.read().strip())
        try:
            os.kill(pid, 0)
            print(f"Scheduler running with PID {pid}")
        except OSError:
            print("Scheduler not running (stale PID file)")
            os.remove('/tmp/slack_bot_scheduler.pid')
    except FileNotFoundError:
        print("Scheduler not running")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python scheduler_launcher.py {start|stop|status}")
        sys.exit(1)

    command = sys.argv[1].lower()

    if command == 'start':
        start_scheduler()
    elif command == 'stop':
        stop_scheduler()
    elif command == 'status':
        status_scheduler()
    else:
        print("Invalid command. Use start, stop, or status")
        sys.exit(1)