from openai import OpenAI
import os
from base64 import b64encode

def summarize_content(text: str, image_path: str, output_file: str) -> None:
    """
    Send text and image to OpenAI for summarization and write the result to a file.
    
    Args:
        text (str): The text to summarize
        image_path (str): Path to the image file
        output_file (str): Path where to save the summary
    """
    # Initialize OpenAI client
    client = OpenAI(api_key=os.getenv("OPEN_API_KEY"))
    
    # Read and encode the image
    with open(image_path, "rb") as image_file:
        image_data = b64encode(image_file.read()).decode('utf-8')
    
    # Prepare the message for GPT-4 Vision
    messages = [
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": f"Please provide a concise summary of this content. Here's the text:\n\n{text}"
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

if __name__ == "__main__":
    summarize_content("some text", "screenshots/Boardgame_Groupwork.png", "test.txt")