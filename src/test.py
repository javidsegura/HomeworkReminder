import subprocess

def create_note_with_checklist(title, checklist_items):
    print("Creating note with checklist")
    
    # Format the checklist items with line breaks for AppleScript
    checklist_content = ''
    for item in checklist_items:
        checklist_content += f"- [ ] {item['name']}\n"
        checklist_content += f"    - Course: {item['course']}\n"
        checklist_content += f"    - Due: {item['due']}\n\n"
    
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

# Example usage
checklist_items = [
    {"name": "Selenium Contest", "course": "BCSAI2024CSAI.2.M.A_C2_464907", "due": "11/09/24, 11:59 PM"},
    {"name": "Database Assignment", "course": "BCSAI2024CSAI.3.M.A_C2_464908", "due": "11/10/24, 5:00 PM"}
]

create_note_with_checklist("Assignments Due on 11/09/24", checklist_items)
