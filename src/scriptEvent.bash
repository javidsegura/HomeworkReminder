# At every hour run main.py, if it is 8pm run main.py every 30 minutes until 12am
# If it is 7am run dailyemail.py

#!/bin/bash

# Get the current hour (24-hour format)
current_hour=$(date +%H)

# Get the current minute
current_minute=$(date +%M)

# Path to your Python scripts
SCRIPT_DIR="/Users/javierdominguezsegura/Programming/College/Sophomore/Databases/Scaper/src"  # Replace with actual path
MAIN_SCRIPT="$SCRIPT_DIR/main.py"
EMAIL_SCRIPT="$SCRIPT_DIR/notifiers/dailyemail.py"

# Run main.py every hour
python3 -m "$MAIN_SCRIPT"

# Special handling for 8 PM to midnight (20:00 - 23:59)
if [ "$current_hour" -ge 20 ] && [ "$current_hour" -lt 24 ]; then
    # If we're at minute 30 or 00, run the script again
    if [ "$current_minute" -eq 30 ] || [ "$current_minute" -eq 0 ]; then
        python3 "$MAIN_SCRIPT"
    fi
fi

# Run dailyemail.py at 7 AM
if [ "$current_hour" -eq 7 ] && [ "$current_minute" -eq 0 ]; then
    python3 -m "$EMAIL_SCRIPT"
fi