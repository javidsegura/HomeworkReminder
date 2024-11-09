import csv 

class CSVFuncs:
    def __init__(self, filename="./utils/assignments.csv"):
        self.filename = filename

    def start_csv(self):
        with open(self.filename, 'w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(
                file, 
                fieldnames=["course_name", "assignment_name", "due_time", "assignment_type"]
            )
            writer.writeheader()
    
    def append_to_csv(self, data):
        with open(self.filename, 'a', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=["course_name", "assignment_name", "due_time", "assignment_type"])
            writer.writerow(data)
        print(f"New assignment added to CSV: {data}")