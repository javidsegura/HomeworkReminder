
#!/bin/bash

while true; do
    clear
    
    # Display menu
    echo "==========================="
    echo "        MAIN MENU         "
    echo "==========================="
    echo "a) Run main.py"
    echo "b) Run dailyemail.py"
    echo "q) Quit"
    echo "==========================="
    
    # Get user input
    read -p "Please select an option: " choice
    
    # Process user input
    case $choice in
        [Aa])
            echo "Running main.py..."
            python3 src/main.py
            read -p "Press Enter to continue..."
            ;;
        [Bb])
            echo "Running dailyemail.py..."
            python3 src/notifiers/dailyemail.py
            read -p "Press Enter to continue..."
            ;;
        [Qq])
            echo "Exiting..."
            exit 0
            ;;
        *)
            echo "Invalid option. Please try again."
            sleep 2
            ;;
    esac
done
