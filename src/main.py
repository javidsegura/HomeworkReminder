from csvFuncs import CSVFuncs

import os
from getpass import getpass
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from ai_prompt import summarize_content

class BlackboardScraper:
    def __init__(self):
        self.driver = webdriver.Chrome()  
        self.wait = WebDriverWait(self.driver, 10)
        self.csv_funcs = CSVFuncs()
        os.makedirs("utils/ai_summaries", exist_ok=True)
        os.makedirs("utils/screenshots", exist_ok=True)

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

        # Wait for MFA completion by checking for Blackboard calendar elements
        found = False
        while not found:
            try:
                calendar_container = self.wait.until(
                    EC.presence_of_element_located((By.ID, "main-content"))
                )
                found = True  # Exit loop when element is found
            except Exception as e:
                print("Still waiting for MFA to be completed...")
                time.sleep(5)  # Retry every 5 seconds
        
      
    def scrapData(self):
        """ scap hw assignments"""    

        try:
            due_dates_tab = self.wait.until(
                EC.element_to_be_clickable((By.ID, "bb-calendar1-deadline"))
            )
            due_dates_tab.click()
        except Exception:
            print("!> Error clicking on the 'Due Dates' tab")
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
            #Today - November 10, 2024Selenium ContestDue date: 11/10/24, 11:59 PM ∙ BCSAI2024CSAI.2.M.A_C2_464907: DESIGNING AND USING DATABASES gotta take only the date
            date = container.find_element(By.CSS_SELECTOR, "span:first-child").text.replace('\n', '')
            print(f"\n=> SCRAPING DATE: {date}")

            due_items = container.find_elements(
                By.CSS_SELECTOR, 
                ".due-item-block .element-card-container .element-card.due-item"
            )
            # each due item is an assignment, test, etc
            for due_item in due_items: 
                print("\n")
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
                    print("!> Could not determine assignment type. Set to 'unknown'.")
        
                # 1) GET ASSIGNMENT NAME
                element_details = due_item.find_element(By.CLASS_NAME, "element-details")

                assignment_name = element_details.find_element(
                    By.CSS_SELECTOR, 
                    ".name a"
                ).text

                print(f"\t=> Scraping: {assignment_name}")

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
                for char in range(len(course_name)):
                    if course_name[char] == " ":
                        course_name = course_name[char+1:]
                        break

                is_graded = False
                max_points = "N/A"
                screenshot_name = "N/A"

                try:
                    link = element_details.find_element(By.CSS_SELECTOR, ".name a")
                    is_clickable = link.is_enabled() and link.is_displayed()
                    
                    if is_clickable:
                        link.click() 
                        time.sleep(2) # wait for sidebar to load
                        
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
                            print(f"\t!> No grading information found for '{assignment_name}'")
                        
                        # Check for footer and take screenshot
                        try:
                            footer = self.driver.find_element(By.ID, "start-attempt-footer")
                            footer_link = footer.find_element(By.TAG_NAME, "a")
                            if footer_link.is_displayed() and footer_link.is_enabled():
                                footer_link.click()
                                time.sleep(1.5) # Give it some time to load the page
                            # Take screenshot
                            screenshot_name = f"utils/screenshots/{assignment_name.replace(' ', '_')}.png"
                            self.driver.save_screenshot(screenshot_name)
                        except Exception:
                            print(f"\t!> No footer found for '{assignment_name}. Can't access the assignment page.")

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
                            "screenshot_name": screenshot_name
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
                            "screenshot_name": screenshot_name
                        })
                except Exception:
                    print(f"\t!> Assignment '{assignment_name}' could not be opened")
                    assignments.append({
                        "course_name": course_name,
                        "assignment_name": assignment_name,
                        "due_time": due_time,
                        "assignment_type": assignment_type,
                        "is_clickable": False,
                        "is_graded": is_graded,
                        "max_points": max_points,
                        "ai_summary": "N/A",
                        "screenshot_name": screenshot_name
                    })
                print(f"\t=> Finished scraping assignment: {assignment_name}", end="\n\t--------------------------------")
            print("\n****************************************************\n")

        if len(assignments) == 0:
            print("No assignments found. Exiting...")
            exit(-1)

        return assignments

    def close(self) -> None:
        self.driver.quit()

def main():
    
    username = os.getenv('BLACKBOARD_USERNAME')
    password = os.getenv('BLACKBOARD_PASSWORD')
    
    scraper = BlackboardScraper()
    try:
        scraper.login(username, password)
        scraper.csv_funcs.start_csv()
        data = scraper.scrapData()
        for assignment in data:
            if assignment["screenshot_name"]: # I only want to summarize assignments that have a screenshot
                summary = summarize_content(assignment, assignment["screenshot_name"], f"utils/ai_summaries/{assignment['assignment_name'].replace(' ', '_')}.txt")
                assignment["ai_summary"] = summary
            scraper.csv_funcs.append_to_csv(assignment)
        print("\n\nCSV created successfully!")
    finally:
        scraper.close()

if __name__ == "__main__":
    main()