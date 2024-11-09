from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import csv
from datetime import datetime
import os
from getpass import getpass
from selenium.webdriver.chrome.options import Options


class BlackboardScraper:
    def __init__(self):
        #chrome_options = Options()
        #chrome_options.add_argument("user-data-dir=/Users/javierdominguezsegura/Library/Application Support/Google/Chrome")  # Adjust with your actual username
        #chrome_options.add_argument("profile-directory=Default") 

        self.driver = webdriver.Chrome()  # Make sure you have ChromeDriver installed
        self.wait = WebDriverWait(self.driver, 10)

    def login(self, username, password):
        # Navigate to the login page
        self.driver.get("https://blackboard.ie.edu/ultra/calendar")
        
        # Wait for and fill in username field
        username_field = self.wait.until(
            EC.presence_of_element_located((By.ID, "i0116"))
        )
        username_field.send_keys(username)
        username_field.send_keys(Keys.RETURN)
        
        # Wait for and fill in password field
        password_field = self.wait.until(
            EC.element_to_be_clickable((By.ID, "i0118"))
        )
        password_field.send_keys(password)
        
        # Find and click the submit button
        submit_button = self.wait.until(
            EC.element_to_be_clickable((By.ID, "idSIButton9"))
        )
        submit_button.click()
        
        print("\nPlease complete the MFA verification in the browser...")
        input("Press Enter after you've completed the MFA verification...")
        print("Continuing with calendar data extraction...")
      
    def get_calendar_data(self):
        # Navigate to calendar page
        
        print("--------------------------------")
        due_dates_tab = self.wait.until(
            EC.element_to_be_clickable((By.ID, "bb-calendar1-deadline"))
        )
        due_dates_tab.click()
        print("Due Dates tab clicked")
        print("Extracting calendar data...") 
        # Wait for and click on Due Dates tab

        deadline_list = self.wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".deadline-list .deadlines .scroll-container > div[bb-scroll]"))
        )
        print("Main deadline container found")

        # Wait for the dynamic content to load
        self.wait.until(
            EC.presence_of_all_elements_located((By.XPATH, ".//div[starts-with(@id, 'bb-calendar1-deadlines-')]"))
        )
        print("Dynamic content loaded")

        # Find all deadline containers for different dates
        deadline_containers = deadline_list.find_elements(
            By.XPATH, 
            "//div[starts-with(@id, 'bb-calendar1-deadlines-')]"
        )
        print(f"Found {len(deadline_containers)} deadline dates")
        
        assignments = []

        for container in deadline_containers:
            # Extract the date from the container's header
            date_header = container.find_element(
                By.CSS_SELECTOR,
                ".date-container .due-date"
            ).text.replace("\n", "")
            print(f"Data header: {date_header}")
            
            # Get all due items within this date container
            due_items = container.find_elements(
                By.CSS_SELECTOR, 
                ".due-item-block .element-card-container .element-card.due-item"
            )
            
            for due_item in due_items:
                element_details = due_item.find_element(By.CLASS_NAME, "element-details")
                
                assignment_name = element_details.find_element(
                    By.CSS_SELECTOR, 
                    ".name a"
                ).text

                content_div = element_details.find_element(By.CLASS_NAME, "content")
                due_time = content_div.find_element(
                    By.CSS_SELECTOR, 
                    "span:first-child"
                ).text.replace("Due date: ", "")

                course_name = content_div.find_element(
                    By.CSS_SELECTOR, 
                    "a"
                ).text

                assignments.append({
                    "full_date": date_header,
                    "course_name": course_name,
                    "assignment_name": assignment_name,
                    "due_time": due_time
                })

        return assignments

    def start_csv(self, filename="assignments.csv"):
        with open(filename, 'w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(
                file, 
                fieldnames=["full_date", "course_name", "assignment_name", "due_time"]
            )
            writer.writeheader()
        print("CSV file has been created successfully!")
    
    def append_to_csv(self, data, filename="assignments.csv"):
        with open(filename, 'a', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=["full_date", "course_name", "assignment_name", "due_time"])
            writer.writerow(data)
        print("Data has been appended to CSV successfully!")

    def close(self):
        self.driver.quit()

def main():
    # You can use environment variables for credentials
    import os
    from getpass import getpass
    
    # Try to get credentials from environment variables
    username = "jdominguez.ieu2023@student.ie.edu" #os.getenv('BLACKBOARD_USERNAME')
    password = "JavierCCAT2305-"                   #os.getenv('BLACKBOARD_PASSWORD')
    
    # If not in environment variables, prompt user
    if not username:
        username = input("Enter your Blackboard username: ")
    if not password:
        password = getpass("Enter your Blackboard password: ")
    
    scraper = BlackboardScraper()
    try:
        #scraper.login(username, password)
        scraper.start_csv()
        data = scraper.get_calendar_data()
        for assignment in data:
            print(assignment)
            scraper.append_to_csv(assignment)
        print("Calendar data has been saved to CSV successfully!")
    finally:
        scraper.close()

if __name__ == "__main__":
    main()