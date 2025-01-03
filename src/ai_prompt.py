from openai import OpenAI
import os
from base64 import b64encode
import json

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
            "content": "You are a helpful assistant that EXPLAINS WHAT THE ASSIGNMENT IS ABOUT \
            Focus on concrete details and requirements rather than generic descriptions. \
            You must respond with valid JSON only. Avoid mentioning the assignment name, course name, or other metadata that's already provided."
        },
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": f"""Analyze this assignment and return a JSON object with the following structure:
                    {{
                        "summary": "string with 2 specific sentences about concrete requirements and deliverables",
                        "estimated_time": "string with time estimate",
                        "difficulty": number between 1-5
                    }}
                    
                    Rules:
                    - The summary must focus on specific tasks and requirements
                    - Do not mention the assignment name or course name
                    - Do not use generic phrases like 'improve your skills' or 'learn about'
                    - If information is not available, use "N/A"
                    
                    Here's the assignment info: {assignment}"""
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
    
    # Extract the summary and clean it up
    content = response.choices[0].message.content

    # Remove markdown code block indicators if present
    content = content.replace('```json', '').replace('```', '').strip()
    
    # Write the cleaned JSON to the output file
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(json.loads(content), f, separators=(',', ':'))
    
    return content

if __name__ == "__main__": # debugging
    mydict = {
        "assignment_name": "Selenium Contest",
        "due_time": "11/10/24, 11:59 PM",
        "course_name": "Web Development",
        "assignment_type": "Quiz",
        "max_points": "100"
    }
    print(summarize_content(mydict, "utils/screenshots/Selenium_Contest.png", "utils/ai_summaries/Selenium_Contest.json"))