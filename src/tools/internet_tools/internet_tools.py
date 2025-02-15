#! /usr/bin/env python3
"""
Internet Tools
Author: Shilpaj Bhalerao
Date: Feb 10, 2025
"""
# Standard Library Imports
import os
import requests
from typing import Optional
from pathlib import Path
import yfinance as yf
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from email.mime.text import MIMEText
import pickle
from datetime import datetime
import base64
import time


def compress_pdf(file_path: str) -> bool:
    api_key = os.getenv('ILOVEPDF_API_KEY')
    if not api_key:
        print("Error: ILOVEPDF_API_KEY is not set.")
        return False

    # 1. Start the session
    session_url = "https://api.ilovepdf.com/v1/start/compress"
    response = requests.post(session_url, json={"public_key": api_key})

    if response.status_code != 200:
        print(f"Error starting session: {response.text}")
        return False

    task = response.json().get("task")

    # 2. Upload the file
    upload_url = "https://api.ilovepdf.com/v1/upload"
    with open(file_path, "rb") as file:
        files = {"file": file}
        response = requests.post(upload_url, data={"task": task}, files=files)

    if response.status_code != 200:
        print(f"Error uploading file: {response.text}")
        return False

    file_server_name = response.json()["server_filename"]

    # 3. Process compression
    process_url = "https://api.ilovepdf.com/v1/process"
    process_data = {
        "task": task,
        "server_filename": file_server_name,
        "output_filename": Path(file_path).name,
    }
    response = requests.post(process_url, data=process_data)

    if response.status_code != 200:
        print(f"Error processing file: {response.text}")
        return False

    # 4. Download compressed file
    download_url = response.json()["download_url"]
    compressed_response = requests.get(download_url)

    if compressed_response.status_code == 200:
        with open(file_path, "wb") as f:
            f.write(compressed_response.content)
        return True
    else:
        print(f"Error downloading file: {compressed_response.text}")
        return False



def compress_image(file_path: str) -> bool:
    """
    Method which uses ILovePDF API to compress an image file
    :param file_path: Path to the image file to compress
    :return: True if the image is compressed successfully, False otherwise
    """
    api_url = "https://api.tinify.com/shrink"
    api_key = os.getenv('ILOVEPDF_API_KEY')  # Replace with your API key
    
    try:
        with open(file_path, "rb") as file:
            response = requests.post(api_url, auth=("api", api_key), files={"file": file})
            
        if response.status_code == 201:
            result_url = response.json()["output"]["url"]
            compressed_file_path = file_path  # Overwrite the original file
            
            # Download the compressed image
            compressed_response = requests.get(result_url)
            with open(compressed_file_path, "wb") as f:
                f.write(compressed_response.content)
            return True
        else:
            print("Compression failed:", response.text)
            return False
    except Exception as e:
        print("Error compressing image:", e)
        return False
    

def send_email(email_subject: str, email_body: str, email_address: str="shilpajbhalerao1994@gmail.com") -> bool:
    """
    Method which uses Gmail API to send an email
    :param email_address: Email address to send the email to
    :param email_subject: Subject of the email
    :param email_body: Body of the email
    :return: True if the email is sent successfully, False otherwise
    """
    try:
        # Check if credentials.json exists
        if not os.path.exists('credentials.json'):
            print("Error: credentials.json file not found. Please follow the setup instructions.")
            return False

        SCOPES = ['https://www.googleapis.com/auth/gmail.send']
        creds = None

        # The file token.pickle stores the user's access and refresh tokens
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)

        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                except Exception as e:
                    print(f"Error refreshing credentials: {str(e)}")
                    # Delete the invalid token.pickle file
                    if os.path.exists('token.pickle'):
                        os.remove('token.pickle')
                    return False
            else:
                try:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        'credentials.json', SCOPES)
                    creds = flow.run_local_server(port=0)
                except Exception as e:
                    print(f"Error during authentication: {str(e)}")
                    print("Please make sure you've set up the OAuth consent screen and added your email as a test user")
                    return False

            # Save the credentials for the next run
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)

        # Create Gmail API service
        service = build('gmail', 'v1', credentials=creds)

        # Create message
        message = MIMEText(email_body)
        message['to'] = email_address
        message['subject'] = email_subject
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
        
        # Send message
        service.users().messages().send(
            userId='me',
            body={'raw': raw_message}
        ).execute()

        print(f"Email sent successfully to {email_address}")
        return True

    except Exception as e:
        print(f"Error sending email: {str(e)}")
        return False


def add_calendar_event(event_name: str, event_date: str, event_start_time: str="12:00 AM", 
                      event_end_time: str="12:00 PM", shared_with: str="shilpajbhalerao1994@gmail.com") -> bool:
    """
    Method which uses Google Calendar API to add an event to the calendar
    :param event_name: Name of the event
    :param event_date: Date of the event
    :param event_start_time: Start time of the event
    :param event_end_time: End time of the event
    :param shared_with: Email address to share the event with
    :return: True if the event is added successfully, False otherwise
    """
    try:
        # Check if credentials.json exists
        if not os.path.exists('credentials.json'):
            print("Error: credentials.json file not found. Please follow the setup instructions.")
            return False

        # Define the scopes for both Gmail and Calendar
        SCOPES = [
            'https://www.googleapis.com/auth/calendar',
            'https://www.googleapis.com/auth/calendar.events'
        ]
        creds = None

        # The file token.pickle stores the user's access and refresh tokens
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)

        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                except Exception as e:
                    print(f"Error refreshing credentials: {str(e)}")
                    # Delete the invalid token.pickle file
                    if os.path.exists('token.pickle'):
                        os.remove('token.pickle')
                    return False
            else:
                try:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        'credentials.json', SCOPES)
                    creds = flow.run_local_server(port=0)
                except Exception as e:
                    print(f"Error during authentication: {str(e)}")
                    print("Please make sure you've set up the OAuth consent screen and added your email as a test user")
                    return False

            # Save the credentials for the next run
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)

        service = build('calendar', 'v3', credentials=creds)

        # Parse date and times
        date_format = "%Y-%m-%d"
        time_format = "%I:%M %p"
        
        try:
            event_date_obj = datetime.strptime(event_date, date_format)
            start_time_obj = datetime.strptime(event_start_time, time_format)
            end_time_obj = datetime.strptime(event_end_time, time_format)
        except ValueError as e:
            print(f"Error parsing date/time: {str(e)}")
            print("Please use format YYYY-MM-DD for date and HH:MM AM/PM for time")
            return False

        start_datetime = event_date_obj.replace(
            hour=start_time_obj.hour,
            minute=start_time_obj.minute
        )
        end_datetime = event_date_obj.replace(
            hour=end_time_obj.hour,
            minute=end_time_obj.minute
        )

        event = {
            'summary': event_name,
            'start': {
                'dateTime': start_datetime.isoformat(),
                'timeZone': 'Asia/Kolkata',  # Using IST timezone
            },
            'end': {
                'dateTime': end_datetime.isoformat(),
                'timeZone': 'Asia/Kolkata',  # Using IST timezone
            },
            'attendees': [
                {'email': shared_with},
            ],
        }

        event = service.events().insert(calendarId='primary', body=event).execute()
        print(f"Event created successfully: {event.get('htmlLink')}")
        return True

    except Exception as e:
        print(f"Error adding calendar event: {str(e)}")
        return False


def share_stock_market_data(stock_symbol: str, time_period: str="1d") -> bool:
    """
    Method which uses Yahoo Finance API to get the stock market data
    :param stock_symbol: Symbol of the stock
    :param time_period: Time period to get the stock data for
    :return: True if the stock data is fetched successfully, False otherwise
    """
    try:
        # Get stock data
        stock = yf.Ticker(stock_symbol)
        
        # Valid periods: 1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max
        hist = stock.history(period=time_period)
        
        if hist.empty:
            print(f"No data found for symbol {stock_symbol}")
            return False
            
        # Save to CSV
        output_file = f"{stock_symbol}_{time_period}_data.csv"
        hist.to_csv(output_file)
        
        print(f"Stock data saved to {output_file}")
        return True
        
    except Exception as e:
        print(f"Error fetching stock data: {str(e)}")
        return False


def send_daily_stock_update(stock_symbol: str = "NVDA", email_address: str = "shilpajbhalerao1994@gmail.com") -> bool:
    """
    Method to fetch today's stock data and send it via email
    :param stock_symbol: Symbol of the stock (default: NVDA)
    :param email_address: Email address to send the update to
    :return: True if the update is sent successfully, False otherwise
    """
    try:
        # Get stock data
        stock = yf.Ticker(stock_symbol)
        
        # Get today's data
        hist = stock.history(period="1d")
        
        if hist.empty:
            print(f"No data found for symbol {stock_symbol}")
            return False
        
        # Format the email body
        current_price = hist['Close'].iloc[-1]
        open_price = hist['Open'].iloc[0]
        high_price = hist['High'].iloc[0]
        low_price = hist['Low'].iloc[0]
        volume = hist['Volume'].iloc[0]
        
        # Calculate price change and percentage
        price_change = current_price - open_price
        price_change_percent = (price_change / open_price) * 100
        
        email_body = f"""
Daily Stock Update for {stock_symbol}

Date: {datetime.now().strftime('%Y-%m-%d')}
Current Price: ${current_price:.2f}
Open Price: ${open_price:.2f}
High: ${high_price:.2f}
Low: ${low_price:.2f}
Volume: {volume:,}

Price Change: ${price_change:.2f} ({price_change_percent:.2f}%)

Note: All prices are in USD.
"""
        
        # Send email
        email_subject = f"Daily Stock Update - {stock_symbol} - {datetime.now().strftime('%Y-%m-%d')}"
        return send_email(email_subject, email_body, email_address)
        
    except Exception as e:
        print(f"Error sending stock update: {str(e)}")
        return False


if __name__ == "__main__":
    # Test the PDF compression
    test_pdf = Path("./dummy.pdf").resolve()
    print(f"Using test file: {test_pdf}")
    
    if not test_pdf.exists():
        print(f"Error: Create a test PDF first at {test_pdf}")
        exit(1)
    
    if not os.getenv('ILOVEPDF_API_KEY'):
        print("Error: Set ILOVEPDF_API_KEY first with:")
        print("export ILOVEPDF_API_KEY='your_api_key'")
        exit(1)
    
    # Run compression
    success = compress_pdf(str(test_pdf))
    print("Compression succeeded" if success else "Compression failed")
