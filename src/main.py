from csvFuncs import CSVFuncs
from ai_prompt import summarize_content
from notifiers.emailNotfiy import EmailNotify

import os
from getpass import getpass
import time
import logging
import pickle
import pathlib

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys


class BlackboardScraper:
    def __init__(self, username: str):
        self.driver = webdriver.Chrome()  
        self.wait = WebDriverWait(self.driver, 10)
        self.csv_funcs = CSVFuncs()
        os.makedirs("utils/ai_summaries", exist_ok=True)
        os.makedirs("utils/screenshots", exist_ok=True)
        os.makedirs("utils/logger", exist_ok=True)
        os.makedirs("utils/cookies", exist_ok=True)
        os.makedirs("utils/csv", exist_ok=True)
        self.cookies_path = pathlib.Path(f"utils/cookies/{username}_cookies.pkl")
    
    def save_cookies(self):
        """Save the current session cookies"""
        with open(self.cookies_path, 'wb') as file:
            pickle.dump(self.driver.get_cookies(), file)
            msg = "Cookies saved successfully"
            print(msg)
            logging.info(msg)

    def load_cookies(self):
        """Load saved cookies if they exist"""
        try:
            with open(self.cookies_path, 'rb') as file:
                cookies = pickle.load(file)
                for cookie in cookies:
                    self.driver.add_cookie(cookie)
                msg = "Cookies loaded successfully"
                print(msg)
                logging.info(msg)
                return True
        except FileNotFoundError:
            msg = "No saved cookies found"
            print(msg)
            logging.info(msg)
            return False

    def set_up_logger(self):
        """Set up logging configuration"""
        # Create directory if it doesn't exist
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        log_filename = f'utils/logger/logger_{timestamp}.log'
        
        logging.basicConfig(
            filename=log_filename,
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

    def login(self, username, password):
        """ pass throught the login page (MFA)"""

        """self.driver.get("https://blackboard.ie.edu")  # First load the base domain for cookies
        
        # If user already logged in, try to use cookies
        if self.load_cookies():
            self.driver.get("https://blackboard.ie.edu/ultra/calendar")
            try:
                # Check if we're still logged in
                calendar_container = self.wait.until(
                    EC.presence_of_element_located((By.ID, "main-content")),
                    timeout=5
                )
                msg = "Successfully logged in using cookies"
                print(msg)
                logging.info(msg)
                return
            except Exception:
                msg = "Cookies expired, proceeding with normal login"
                print(msg)
                logging.info(msg)"""
                
        # No cookies found, proceed with normal login
        try:
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
            self.save_cookies()

        except Exception as e:
            msg = f"Error logging in: {e}"
            print(msg)
            logging.error(msg)
            exit(-1)

        # Wait for MFA completion by checking for Blackboard calendar elements
        found = False
        while not found:
            try:
                calendar_container = self.wait.until(
                    EC.presence_of_element_located((By.ID, "main-content"))
                )
                found = True  # Exit loop when element is found
            except Exception as e:
                msg = "Still waiting for MFA to be completed..."
                print(msg)
                logging.info(msg)
                time.sleep(5)  # Retry every 5 seconds
        
      
    def scrapData(self):
        """ scap hw assignments . missing to check if element already in df in order to avoid redundancy"""    

        try:
            due_dates_tab = self.wait.until(
                EC.element_to_be_clickable((By.ID, "bb-calendar1-deadline"))
            )
            due_dates_tab.click()
        except Exception:
            msg = "!> Error clicking on the 'Due Dates' tab"
            print(msg)
            logging.error(msg)
            exit(-1)
       
        deadline_list = self.wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".deadline-list .deadlines .scroll-container > div[bb-scroll]"))
        )

        # Wait for the dynamic content to load
        self.wait.until(
            EC.presence_of_all_elements_located((By.XPATH, ".//div[starts-with(@id, 'bb-calendar1-deadlines-')]"))
        )

        deadline_containers = deadline_list.find_elements(
            By.XPATH, 
            "//div[starts-with(@id, 'bb-calendar1-deadlines-')]" # this dynamically finds all divs that have their id starting with bb-calendar1-deadlines-
        )
        
        assignments = []
        # each container is a different date
        for container in deadline_containers: 
            date = container.find_element(By.CSS_SELECTOR, "span:first-child").text.replace('\n', '')
            msg = f"\n=> SCRAPING DATE: {date}"
            print(msg)
            logging.info(msg)

            due_items = container.find_elements(
                By.CSS_SELECTOR, 
                ".due-item-block .element-card-container .element-card.due-item"
            )
            # each due item is an assignment, test, etc
            for due_item in due_items: 
                print("\n")
                logging.info("")

                # 0) CATEGORIZE ASSIGNMENT TYPE
                element_image = due_item.find_element(By.CLASS_NAME, "element-image")
                icon_container = element_image.find_element(By.TAG_NAME, "bb-ui-content-icon")
                ng_switch_div = icon_container.find_element(By.CSS_SELECTOR, "div[ng-switch]")

                try:
                    icon_element = ng_switch_div.find_element(
                        By.XPATH, 
                        ".//*[starts-with(local-name(), 'bb-ui-icon-large-')]"
                    )
                    tag_name = icon_element.tag_name
                    assignment_type = tag_name.replace('bb-ui-icon-large-', '') # remove prefix
                except Exception:
                    assignment_type = "unknown"
                    msg = "!> Could not determine assignment type. Set to 'unknown'."
                    print(msg)
                    logging.warning(msg)
        
                # 1) GET ASSIGNMENT NAME
                element_details = due_item.find_element(By.CLASS_NAME, "element-details")

                assignment_name = element_details.find_element(
                    By.CSS_SELECTOR, 
                    ".name a"
                ).text

                msg = f"\t=> Scraping: {assignment_name}"
                print(msg)
                logging.info(msg)

                # 2) GET DUE DATE
                content_div = element_details.find_element(By.CLASS_NAME, "content")
                due_time = content_div.find_element(
                    By.CSS_SELECTOR, 
                    "span:first-child"
                ).text.replace("Due date: ", "") # remove prefix

                # 3) GET COURSE NAME
                course_name = content_div.find_element(
                    By.CSS_SELECTOR, 
                    "a"
                ).text

                # Remove the first word from the course name    
                for char in range(len(course_name)):
                    if course_name[char] == " ":
                        course_name = course_name[char+1:]
                        break

                # If the assignment was already scraping, skip it 
                checking = self.csv_funcs.check_add(course_name, assignment_name) # returns true if u can write
                if not checking:
                    msg = f"\t!> Assignment '{assignment_name}' already exists in the CSV. Skipping..."
                    print(msg)
                    logging.warning(msg)
                    continue
                print(f"CHECKING {checking}")

                is_graded = False
                max_points = "N/A"
                screenshot_name = "N/A"
                link = "N/A"

                try:
                    link = element_details.find_element(By.CSS_SELECTOR, ".name a")
                    is_clickable = link.is_enabled() and link.is_displayed()
                    
                    if is_clickable:
                        # Get the actual URL from the data-href attribute or other possible attributes
                        link_url = "N/A" # is this needed?
                        link.click()
                        time.sleep(2) # wait for sidebar to load
                        link_url = self.driver.current_url
                        
                        # 4) GET GRADING INFO
                        try:
                            grading_section = self.driver.find_element(By.CLASS_NAME, "no-submission-card")
                            if "Maximum points" in grading_section.text:  
                                is_graded = True
                                points_element = grading_section.find_element(
                                    By.CSS_SELECTOR, 
                                    ".no-submission-value span bdi"
                                )
                                max_points = float(points_element.text)
                        except Exception:
                            msg = f"\t!> No grading information found for '{assignment_name}'"
                            print(msg)
                            logging.warning(msg)
                        
                        # Check for footer and take screenshot
                        try:
                            footer = self.driver.find_element(By.ID, "start-attempt-footer")
                            footer_link = footer.find_element(By.TAG_NAME, "a")
                            if footer_link.is_displayed() and footer_link.is_enabled():
                                footer_link.click()
                                time.sleep(2) # Give it some time to load the page
                            # Take screenshot
                            screenshot_name = f"utils/screenshots/{assignment_name.replace(' ', '_')}.png"
                            self.driver.save_screenshot(screenshot_name)
                            if link_url == "javascript:void(0)": 
                                link_url = self.driver.current_url
                        except Exception:
                            msg = f"\t!> No footer found for '{assignment_name}. Can't access the assignment page."
                            print(msg)
                            logging.warning(msg)

                        # Close the panel (same inside and outside the assignment page)
                        close_button = self.wait.until(
                            EC.element_to_be_clickable((By.CSS_SELECTOR, "button.bb-close"))
                        )
                        close_button.click()
                        
                        assignments.append({
                            "course_name": course_name,
                            "assignment_name": assignment_name,
                            "due_time": due_time,
                            "assignment_type": assignment_type,
                            "is_clickable": is_clickable,
                            "is_graded": is_graded,
                            "max_points": max_points,
                            "ai_summary": "N/A",
                            "screenshot_name": screenshot_name,
                            "link": link_url
                        })
                    else:
                        assignments.append({
                            "course_name": course_name,
                            "assignment_name": assignment_name,
                            "due_time": due_time,
                            "assignment_type": assignment_type,
                            "is_clickable": is_clickable,
                            "is_graded": is_graded,
                            "max_points": max_points,
                            "ai_summary": "N/A",
                            "screenshot_name": screenshot_name,
                            "link": "N/A"
                        })
                except Exception:
                    msg = f"\t!> Assignment '{assignment_name}' could not be opened"
                    print(msg)
                    logging.warning(msg)
                    assignments.append({
                        "course_name": course_name,
                        "assignment_name": assignment_name,
                        "due_time": due_time,
                        "assignment_type": assignment_type,
                        "is_clickable": False,
                        "is_graded": is_graded,
                        "max_points": max_points,
                        "ai_summary": "N/A",
                        "screenshot_name": screenshot_name,
                        "link": "N/A"
                    })
                msg = f"\t=> Finished scraping assignment: {assignment_name}\n"
                print(msg, "\t--------------------------------")
                logging.info(msg)
            msg = "\n****************************************************\n"
            print(msg)

        if len(assignments) == 0:
            msg = "No (new) assignments found. Exiting..."
            print(msg)
            logging.error(msg)
            exit(0)

        return assignments

    def close(self) -> None:
        self.driver.quit()

def main():
    
    username = os.getenv('BLACKBOARD_USERNAME')
    password = os.getenv('BLACKBOARD_PASSWORD')

    if not username:
        username = input("Enter your Blackboard username: ")
    if not password:
        password = getpass("Enter your Blackboard password: ")
    
    scraper = BlackboardScraper(username)
    scraper.set_up_logger()

    notifier = EmailNotify(credentials_file="utils/OAuth/credentials.json")

    try:
        scraper.login(username, password)
        df = scraper.csv_funcs.start_csv()
        data = scraper.scrapData()
        for assignment in data:
            if assignment["screenshot_name"] != "N/A": # I only want to summarize assignments that have a screenshot (for now)
                print(f"Summarizing {assignment['assignment_name']}")
                logging.info(f"Summarizing {assignment['assignment_name']}")
                summary = summarize_content(assignment, assignment["screenshot_name"], f"utils/ai_summaries/{assignment['assignment_name'].replace(' ', '_')}.json")
                assignment["ai_summary"] = summary
            scraper.csv_funcs.append_to_csv(assignment)
            notifier.send_email(assignment, assignment["screenshot_name"])
        msg = "\n\nCSV created successfully!"
        print(msg)
        logging.info(msg)
    finally:
        scraper.close()
        scraper.csv_funcs.write_to_csv()



if __name__ == "__main__":
    main()