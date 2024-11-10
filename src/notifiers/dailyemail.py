import os
import base64
from email.message import EmailMessage
from google.oauth2 import service_account
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from google.auth.transport import Request
import mimetypes
from google_auth_oauthlib.flow import InstalledAppFlow  
from google.oauth2.credentials import Credentials  
import json
from datetime import datetime
import pandas as pd 


credentials_file = "utils/OAuth/credentials.json"

def authenticate():
        creds = None
        # Check if token.json exists and load credentials
        if os.path.exists("utils/OAuth/token.json"):
            try:
                with open("utils/OAuth/token.json", "r") as token_file:
                    creds_data = json.load(token_file)
                    creds = Credentials.from_authorized_user_info(creds_data)
                    
                    # If credentials are valid, return the service immediately
                    if creds and creds.valid:
                        return build("gmail", "v1", credentials=creds)
            except Exception as e:
                print(f"Error loading credentials: {e}")
                creds = None
        else:
            # Only proceed with OAuth flow if necessary
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        credentials_file, 
                        ["https://www.googleapis.com/auth/gmail.send"]
                    )
                    creds = flow.run_local_server(port=0)
                
                # Save the credentials for future use
                with open("utils/OAuth/token.json", "w") as token_file:
                    token_file.write(creds.to_json())
        
        return build("gmail", "v1", credentials=creds)


def send_daily_email() -> None:
        """ read the csv, get the ones dues today, and send a single email with name, due date and link"""
        df = pd.read_csv("utils/csv/assignments.csv")
        today = datetime.now().strftime("%m/%d/%y") # time is of format: 11/10/24, 11:59 PM
        assignments_today = df[df['due_time'].str.contains(today)]
        service = authenticate()

        message = EmailMessage()
      
        message["Subject"] = f"Daily Blackboard Summary: {today}"
        message["From"] = "me"
        message["To"] = "jdominguez.ieu2023@student.ie.edu"
        
        msg_content = f"""
            ━━━━━━━━━━━━━━━━━━━━
            🎓 Daily Assignment Summary for {today}
            ━━━━━━━━━━━━━━━━━━━━

            """
            
        if len(assignments_today) == 0:
            msg_content += "No assignments due today! 🎉\n"
        else:
                  for _, assignment in assignments_today.iterrows():
                        due_datetime = datetime.strptime(assignment['due_time'], "%m/%d/%y, %I:%M %p")
                        time_remaining = due_datetime - datetime.now()
                        days_remaining = time_remaining.days
                        hours_remaining = time_remaining.seconds // 3600
                        
                        msg_content += f"""
            📚 {assignment['course_name']}
            Assignment: {assignment['assignment_name']}
            Due: {assignment['due_time']}
            Time Remaining: {days_remaining} days, {hours_remaining} hours
            Link: {assignment['link']}
            """

        msg_content += """
            ━━━━━━━━━━━━━━━━━━━━
            Have a productive day! 💪
            """    
        message.set_content(msg_content)

        # Encode the email message
        encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

        # Send the email
        try:
            service.users().messages().send(userId="me", body={"raw": encoded_message}).execute()
            print("Email sent successfully.")
        except Exception as e:
            print(f"Failed to send email: {e}")
             
send_daily_email()