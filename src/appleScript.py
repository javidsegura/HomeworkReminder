import csv
import subprocess
from datetime import datetime

def create_note_with_checklist(title, checklist_items):
    print("Creating note with checklist")
    # Format the checklist items for AppleScript
    checklist_content = ''.join([f"- [ ] {item}\n" for item in checklist_items])
    
    # AppleScript to create a new note with a checklist
    applescript = f'''
    tell application "Notes"
        tell account "iCloud"
            tell folder "Notes"
                make new note with properties {{name:"{title}", body:"{checklist_content}"}}
            end tell
        end tell
    end tell
    '''
    # Execute the AppleScript
    subprocess.run(['osascript', '-e', applescript])

def main():
    today = datetime.now().strftime("%m/%d/%y")  # Get today's date in the format used in the CSV
    checklist_items = []

    # Read the CSV file
    with open('./utils/assignments.csv', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for assignment in reader:
            # Check if the assignment is due today
            due_date = assignment['due_time'].split(',')[0].strip()
            if due_date == today:
                # Format the checklist item
                item = f"name: {assignment['assignment_name']}, course: {assignment['course_name']}, due: {assignment['due_time']}"
                checklist_items.append(item)

    # Create a note if there are any items due today
    if checklist_items:
        title = f"Assignments Due on {today}"
        create_note_with_checklist(title, checklist_items)

main()