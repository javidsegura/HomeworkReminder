
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
from google_auth_oauthlib.flow import InstalledAppFlow  # Add this import
from google.oauth2.credentials import Credentials  # Add this import
import json

class EmailNotify:
    def __init__(self, credentials_file: str):
        self.credentials_file = credentials_file
        self.service = self.authenticate()

    def authenticate(self):
        creds = None
        if os.path.exists("utils/OAuth/token.json"):
            with open("utils/OAuth/token.json", "r") as token_file:
                # Change this line - we're using OAuth2 credentials, not service account
                creds = json.load(token_file)
                creds = Credentials.from_authorized_user_info(creds)
        
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

    def send_email(self, body: dict, image_path: str) -> None:
        message = EmailMessage()
        message.set_content("\n".join([f"{key}: {value}" for key, value in body.items()]))
        message["Subject"] = "Assignment Notification"
        message["From"] = "me"
        message["To"] = "jdominguez.ieu2023@student.ie.edu"

        # Attach image if available
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
            print("Email sent successfully.")
        except Exception as e:
            print(f"Failed to send email: {e}")


# Usage example
if __name__ == "__main__":
    assignments = [
        {"title": "Math Homework", "due_date": "2024-12-01"},
        {"title": "Science Project", "due_date": "2024-12-10"},
    ]
    images = ["math_homework.png", "science_project.png"]

    email_notify = EmailNotify("utils/OAuth/credentials.json")
    for assignment, image in zip(assignments, images):
        email_notify.send_email(assignment, image)
        print("\n")
