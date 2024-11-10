
""" For each assignment dict and its corresponding image, send an email with the assignment details from 
your own gmail to your own gmail"""

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


class EmailNotify:
    def __init__(self, credentials_file: str):
        self.credentials_file = credentials_file
        self.service = self.authenticate()

    def authenticate(self):
        creds = None
        # Check if token.json exists and load credentials
        if os.path.exists("utils/OAuth/token.json"):
            print("Token found, loading credentials")
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
                        self.credentials_file, 
                        ["https://www.googleapis.com/auth/gmail.send"]
                    )
                    creds = flow.run_local_server(port=0)
                
                # Save the credentials for future use
                with open("utils/OAuth/token.json", "w") as token_file:
                    token_file.write(creds.to_json())
        
        return build("gmail", "v1", credentials=creds)

    def send_email(self, content: dict, image_path: str) -> None:
        message = EmailMessage()
        
        # Parse AI summary from JSON string
        if content['ai_summary'] != "N/A":
            ai_summary = json.loads(content['ai_summary'])
        else:
            ai_summary = {"summary": "N/A", "estimated_time": "N/A", "difficulty": 0}

        complexity_stars = "⭐" * ai_summary['difficulty']
        
        # Calculate time remaining
        due_datetime = datetime.strptime(content['due_time'], "%m/%d/%y, %I:%M %p")
        time_remaining = due_datetime - datetime.now()
        days_remaining = time_remaining.days
        hours_remaining = time_remaining.seconds // 3600
        
        # Format countdown message
        countdown_msg = f"{days_remaining} days, {hours_remaining} hours remaining"
        if days_remaining < 0:
            countdown_msg = "OVERDUE!"
        elif days_remaining == 0 and hours_remaining < 24:
            countdown_msg = "⚠️ DUE TODAY! ⚠️"
        
        if content['assignment_type'].upper() == "DOCUMENT-BLANK":
            assignment_type = "ASSIGNMENT CONTENT"
        elif content['assignment_type'].upper() == "ASSIGNMENTS":
            assignment_type = "ASSIGNMENT"
        else:
            assignment_type = content['assignment_type'].upper()

        message["Subject"] = f"NEW {assignment_type} in Blackboard: {content['course_name']} - {content['assignment_name']}"
        message["From"] = "me"
        message["To"] = "jdominguez.ieu2023@student.ie.edu"
        
        msg_content = f"""
        📚 Assignment Details
        ━━━━━━━━━━━━━━━━━━━━

        📝 Description: {ai_summary["summary"]}

        ⏰ Due: {content['due_time']}
        ⏳ Time Remaining: {countdown_msg}

        🔗 Assignment Link:
            {content['link']}

        📊 Assignment Info:
        • Complexity: {complexity_stars}
        • Expected Duration: {ai_summary["estimated_time"]}
        • Graded: {"Yes (" + str(content['max_points']) + " points)" if content['is_graded'] else "No"}

        ━━━━━━━━━━━━━━━━━━━
        Good luck with your assignment! 🍀
        """
        message.set_content(msg_content)

        # Attach image if available
        if image_path != "N/A":
            if os.path.exists(image_path):
                with open(image_path, "rb") as img_file:
                    img_data = img_file.read()
                    img_type, _ = mimetypes.guess_type(image_path)
                    maintype, subtype = img_type.split("/")
                    message.add_attachment(img_data, maintype=maintype, subtype=subtype, filename=os.path.basename(image_path)) 

        # Encode the email message
        encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

        # Send the email
        try:
            self.service.users().messages().send(userId="me", body={"raw": encoded_message}).execute()
            print("\nEmail sent successfully.")
        except Exception as e:
            print(f"Failed to send email: {e}")



# Usage example
if __name__ == "__main__":
    assignments = [
        {
            "course_name": "test", 
            "assignment_name": "test", 
            "due_time": "11/10/24, 11:59 PM", 
            "assignment_type": "test", 
            "is_clickable": "test", 
            "is_graded": "test", 
            "max_points": "test", 
            "ai_summary": '{"summary": "test2", "estimated_time": "test3", "difficulty": 2}',  # Fixed the JSON string
            "screenshot_name": "test", 
            "link": "test"
        }
    ]
    email_notify = EmailNotify("utils/OAuth/credentials.json")
    for assignment in assignments:
        email_notify.send_email(assignment, assignment["screenshot_name"])
        print("\n")