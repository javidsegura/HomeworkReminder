
from csvFuncs import CSVFuncs

import os
from getpass import getpass

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options

class BlackboardScraper:
    def __init__(self):
        #chrome_options = Options()
        #chrome_options.add_argument("user-data-dir=/Users/javierdominguezsegura/Library/Application Support/Google/Chrome")  # Adjust with your actual username
        #chrome_options.add_argument("profile-directory=Default") 
        self.driver = webdriver.Chrome()  # Make sure you have ChromeDriver installed
        self.wait = WebDriverWait(self.driver, 10)
        self.csv_funcs = CSVFuncs()

    def login(self, username, password):
        """ pass throught the login page (MFA)"""
        self.driver.get("https://blackboard.ie.edu/ultra/calendar")
        
        username_field = self.wait.until(
            EC.presence_of_element_located((By.ID, "i0116"))
        )
        username_field.send_keys(username)
        username_field.send_keys(Keys.RETURN)
        
        password_field = self.wait.until(
            EC.element_to_be_clickable((By.ID, "i0118"))
        )
        password_field.send_keys(password)
        
        # Find and click the submit button
        submit_button = self.wait.until(
            EC.element_to_be_clickable((By.ID, "idSIButton9"))
        )
        submit_button.click()
        
        input("Press Enter after you've completed the MFA verification: ")
      
    def scrapData(self):
        """ scap hw assignments"""        

        print("--------------------------------")
        due_dates_tab = self.wait.until(
            EC.element_to_be_clickable((By.ID, "bb-calendar1-deadline"))
        )
        due_dates_tab.click()
       
        deadline_list = self.wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".deadline-list .deadlines .scroll-container > div[bb-scroll]"))
        )

        # Wait for the dynamic content to load
        self.wait.until(
            EC.presence_of_all_elements_located((By.XPATH, ".//div[starts-with(@id, 'bb-calendar1-deadlines-')]"))
        )

        # Find all deadline containers for different dates
        deadline_containers = deadline_list.find_elements(
            By.XPATH, 
            "//div[starts-with(@id, 'bb-calendar1-deadlines-')]"
        )
        
        # Iterate over all the deadline containers
        assignments = []
        for container in deadline_containers: 
            due_items = container.find_elements(
                By.CSS_SELECTOR, 
                ".due-item-block .element-card-container .element-card.due-item"
            )
            
            # Iterate over all the due items (assignments, tests, etc) within this date container
            for due_item in due_items:
                
                element_image = due_item.find_element(By.CLASS_NAME, "element-image")
                # Find bb-ui-content-icon first
                icon_container = element_image.find_element(By.TAG_NAME, "bb-ui-content-icon")
                
                # Wait for the ng-switch div to be present
                ng_switch_div = icon_container.find_element(By.CSS_SELECTOR, "div[ng-switch]")
                
                try:
                    # Look for any element whose tag name starts with bb-ui-icon-large- inside ng-switch div
                    icon_element = ng_switch_div.find_element(
                        By.XPATH, 
                        ".//*[starts-with(local-name(), 'bb-ui-icon-large-')]"
                    )
                    
                    # Get the type from the tag name by removing the prefix
                    tag_name = icon_element.tag_name
                    assignment_type = tag_name.replace('bb-ui-icon-large-', '')
                    print(f"Assignment Type: {assignment_type}")
                except:
                    assignment_type = "unknown"
                    print("Could not determine assignment type")
                     

                element_details = due_item.find_element(By.CLASS_NAME, "element-details")
                # Getting info of assignment
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
                    "course_name": course_name,
                    "assignment_name": assignment_name,
                    "due_time": due_time,
                    "assignment_type": assignment_type
                })

        

        return assignments

    def close(self):
        self.driver.quit()

def main():
    
    username = os.getenv('BLACKBOARD_USERNAME')
    password = os.getenv('BLACKBOARD_PASSWORD')
    
    if not username:
        username = input("Enter your Blackboard username: ")
    if not password:
        password = getpass("Enter your Blackboard password: ")
    
    scraper = BlackboardScraper()
    try:
        scraper.login(username, password)
        scraper.csv_funcs.start_csv()
        data = scraper.scrapData()
        for assignment in data:
            scraper.csv_funcs.append_to_csv(assignment)
        print("CSV created successfully!")
    finally:
        scraper.close()

if __name__ == "__main__":
    main()