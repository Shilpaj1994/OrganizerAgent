#! /usr/bin/env python3
"""
Script to schedule the stock update task
Author: Shilpaj Bhalerao
Date: Feb 15, 2025
"""
# Standard Library Imports
import time

# Third Party Imports
import schedule

# Local Imports
from src.tools.internet_tools.internet_tools import send_daily_stock_update


def job():
    """
    Method to schedule the stock update task
    """
    send_daily_stock_update()

# Schedule the job to run at 5 PM every day
schedule.every().day.at("17:00").do(job)

while True:
    schedule.run_pending()
    time.sleep(60)  # Check every minute 