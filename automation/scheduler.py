import os
import sys
import logging
from datetime import datetime
from apscheduler.schedulers.blocking import BlockingScheduler

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from automation.run_pipeline import run


logging.basicConfig(level="INFO")

scheduler = BlockingScheduler()
# runs immediately on startup, then every 30 minutes
scheduler.add_job(run, "interval", minutes=30, next_run_time=datetime.now())

if __name__ == "__main__":
    print("Automation scheduler started. Running every 30 minutes. Press Ctrl+C to stop.")
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        print("Automation scheduler stopped.")
