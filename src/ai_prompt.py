from openai import OpenAI
import os
from base64 import b64encode

def summarize_content(assignment: dict, image_path: str, output_file: str) -> str:
    """ Send image and text for LLM summarization """
    # Initialize OpenAI client
    client = OpenAI(api_key=os.getenv("OPEN_API_KEY"))
    
    # Read and encode the image
    with open(image_path, "rb") as image_file:
        image_data = b64encode(image_file.read()).decode('utf-8')
    
    # Prepare the message for GPT-4 Vision
    messages = [
        {
            "role": "system",
            "content": "You are a helpful assistant that summarizes homework assignments. You \
            will be given an image of an assignment and some information about it. VERY IMPORTANT TO \
            PROVIDE NEW INFORMATION, NOT JUST REPEAT WHAT IS GIVEN TO YOU."
        },
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": f"""This is the info on my assignment: Assignment name: {assignment['assignment_name']}\nDue date: {assignment['due_time']}, 
                    course name: {assignment['course_name']}, assignment type: {assignment['assignment_type']}, max points: {assignment['max_points']} 
                    . Return a JSON in a single line with the following information: 
                    - summary of the assignment (2-3 sentences)
                    - estimated time it will take to complete the assignment
                    - estimated difficulty of the assignment (1-5)"""
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/png;base64,{image_data}"
                    }
                }
            ]
        }
    ]
    
    # Make the API call
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        max_tokens=500
    )
    
    # Extract the summary
    summary = response.choices[0].message.content
    
    # Write the summary to the output file
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(summary)
    return summary
