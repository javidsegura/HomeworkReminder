import csv 
import os
import pandas as pd
class CSVFuncs:
    """ Load pandas and work on it, after end of session write to csv"""

    def __init__(self, filename="./utils/csv/assignments.csv"):
        self.filename = filename
        self.df = None

    def start_csv(self) -> None:
        """ when starting check if any experired and delete them from system. """
        if os.path.exists(self.filename):
            self.df = pd.read_csv(self.filename)
            return self.df
        try:
            with open(self.filename, 'w', newline='', encoding='utf-8') as file:
                writer = csv.DictWriter(
                file, 
                fieldnames=["course_name", "assignment_name", "due_time", "assignment_type", "is_clickable", 
                            "is_graded", "max_points", "ai_summary", "screenshot_name", "link"]
                )
                writer.writeheader()
            self.df = pd.read_csv(self.filename)
            return self.df
        except Exception as e:
            print(f"Error starting CSV: {e}")
    
    def check_add(self, course_name: str, assignment_name: str) -> bool:
        """ check if the assignment already exists in the csv"""
        if self.df is not None:
            return self.df[(self.df['course_name'] == course_name) & (self.df['assignment_name'] == assignment_name)].empty # True if not exists, false if exists
        raise ValueError("DataFrame is not initialized")
    
    def append_to_csv(self, data: dict) -> None:
        try:
            if self.df is not None:  # Changed from 'if self.df:'
                self.df = pd.concat([self.df, pd.DataFrame([data])], ignore_index=True) 
        except Exception as e:
            print(f"Error appending to CSV: {e}")
    
    def write_to_csv(self) -> None:
        if self.df is not None:
            self.df.to_csv(self.filename, index=False)
        else:
            raise ValueError("DataFrame is not initialized") 
        
if __name__ == "__main__":
    csv_funcs = CSVFuncs()
    csv_funcs.start_db()
    csv_funcs.append_to_db({"course_name": "test", "assignment_name": "test", "due_time": "test", "assignment_type": "test", "is_clickable": "test", "is_graded": "test", "max_points": "test", "ai_summary": "test", "screenshot_name": "test", "link": "test"})
    print(csv_funcs.df)
    csv_funcs.write_to_csv()
  