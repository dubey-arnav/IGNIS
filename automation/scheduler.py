import os
import sys
import logging
from datetime import datetime
from apscheduler.schedulers.blocking import BlockingScheduler

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from automation.run_pipeline import run


logging.basicConfig(level=os.getenv("AUTOMATION_LOG_LEVEL", "INFO"))

interval_minutes = int(os.getenv("AUTOMATION_INTERVAL_MINUTES", "30"))

scheduler = BlockingScheduler()
# runs immediately on startup, then every interval_minutes
scheduler.add_job(run, "interval", minutes=interval_minutes, next_run_time=datetime.now())

if __name__ == "__main__":
    print(f"Automation scheduler started. Running every {interval_minutes} minutes. Press Ctrl+C to stop.")
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        print("Automation scheduler stopped.")
