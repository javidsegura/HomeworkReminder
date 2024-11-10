import csv 

class CSVFuncs:
    def __init__(self, filename="./utils/assignments.csv"):
        self.filename = filename

    def start_csv(self) -> None:
        try:
            with open(self.filename, 'w', newline='', encoding='utf-8') as file:
                writer = csv.DictWriter(
                file, 
                fieldnames=["course_name", "assignment_name", "due_time", "assignment_type", "is_clickable", 
                            "is_graded", "max_points", "ai_summary", "screenshot_name"]
                )
                writer.writeheader()
        except Exception as e:
            print(f"Error starting CSV: {e}")
    
    def append_to_csv(self, data: dict) -> None:
        try:
            with open(self.filename, 'a', newline='', encoding='utf-8') as file:
                writer = csv.DictWriter(file, fieldnames=["course_name", "assignment_name", "due_time", "assignment_type", "is_clickable", 
                                                      "is_graded", "max_points", "ai_summary", "screenshot_name"])
                writer.writerow(data)
            print(f"New assignment added to CSV: {data}")
        except Exception as e:
            print(f"Error appending to CSV: {e}")
  
