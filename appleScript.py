import csv
import subprocess

def create_note_in_notes_app(title, content):
    # AppleScript to create a new note
    applescript = f'''
    tell application "Notes"
        tell account "iCloud"
            tell folder "Notes"
                make new note with properties {{name:"{title}", body:"{content}"}}
            end tell
        end tell
    end tell
    '''
    # Execute the AppleScript
    subprocess.run(['osascript', '-e', applescript])

def main():
    # Read the CSV file
    with open('assignments.csv', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            # Prepare the title and content for the note
            title = f"{row['course_name']} - {row['assignment_name']}"
            content = f"Due Date: {row['full_date']} at {row['due_time']}\n\nCourse: {row['course_name']}\nAssignment: {row['assignment_name']}"
            
            # Create a note in the Notes app
            create_note_in_notes_app(title, content)

if __name__ == "__main__":
    main()