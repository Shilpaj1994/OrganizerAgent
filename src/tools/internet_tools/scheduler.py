#! /usr/bin/env python3
"""
This module provides a simple interface for scheduling emails to be sent at a given time.
Author: Shilpaj Bhalerao
Date: Feb 16, 2025
"""
# Standard Library Imports
import argparse
from datetime import datetime, timedelta
import time

# Local Imports
from internet_tools import send_daily_stock_update


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--recipient", type=str, required=True)
    parser.add_argument("--stock_symbol", type=str, default="NVDA")
    parser.add_argument("--scheduled_time", type=str, default="17:00")
    args = parser.parse_args()

    while True:  # Run continuously
        try:
            # Parse scheduled time
            scheduled_time = datetime.strptime(args.scheduled_time, "%H:%M")
            
            # Get current time
            current_time = datetime.now()
            
            # Set scheduled time for today
            scheduled_datetime = current_time.replace(
                hour=scheduled_time.hour,
                minute=scheduled_time.minute,
                second=0,
                microsecond=0
            )

            # If scheduled time has passed today, set it for tomorrow
            if scheduled_datetime < current_time:
                scheduled_datetime += timedelta(days=1)

            # Calculate seconds to wait
            wait_seconds = (scheduled_datetime - current_time).total_seconds()
            print(f"Next update scheduled for {scheduled_datetime.strftime('%Y-%m-%d %H:%M')}")
            print(f"Waiting {wait_seconds:.0f} seconds...")

            # Sleep until scheduled time
            time.sleep(wait_seconds)

            # Send the update at scheduled time
            result = send_daily_stock_update(
                recipient=args.recipient,
                stock_symbol=args.stock_symbol,
                scheduled_time=args.scheduled_time
            )
            
            print(f"Status: {result['statusCode']}")
            print(f"Response: {result['body']}")

        except KeyboardInterrupt:
            print("\nScheduler stopped by user")
            break
        except Exception as e:
            print(f"Error occurred: {str(e)}")
            print("Retrying in 60 seconds...")
            time.sleep(60)


if __name__ == "__main__":
    main()