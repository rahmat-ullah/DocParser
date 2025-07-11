import pytesseract
from PIL import Image
import openai
import os
from dotenv import load_dotenv

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

def extract_table_from_image(image_path: str) -> str | None:
    """
    Extracts text from an image using OCR and then uses an LLM to
    identify and format any tables found in the text into Markdown.

    Args:
        image_path: Path to the image file.

    Returns:
        A string containing the Markdown formatted table, or None if no table is found
        or an error occurs.
    """
    try:
        # Step 1: Extract text from image using Tesseract OCR
        img = Image.open(image_path)
        raw_text = pytesseract.image_to_string(img)

        if not raw_text.strip():
            print("No text detected in the image.")
            return None

        # Step 2: Use LLM to identify and format tables
        prompt = f"""The following text was extracted from an image.
Please identify any tables in this text and format them as Markdown tables.
If no table is found, respond with "No table found".

Raw text:
---
{raw_text}
---
Markdown table:
"""

        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that extracts tables from text and formats them in Markdown."},
                {"role": "user", "content": prompt}
            ]
        )

        markdown_table = response.choices[0].message.content.strip()

        if markdown_table.lower() == "no table found":
            return None

        return markdown_table

    except FileNotFoundError:
        print(f"Error: Image file not found at {image_path}")
        return None
    except pytesseract.TesseractNotFoundError:
        print("Error: Tesseract is not installed or not in your PATH.")
        print("Please install Tesseract and make sure it's accessible.")
        return None
    except openai.APIError as e:
        print(f"OpenAI API Error: {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None

if __name__ == '__main__':
    # This is a placeholder for testing.
    # The actual test script will be created in a separate step.
    print("Please set OPENAI_API_KEY in your .env file")
    # Example usage (requires a test image and API key):
    # table_md = extract_table_from_image("path/to/your/image.png")
    # if table_md:
    #     print(table_md)
    # else:
    #     print("No table extracted or an error occurred.")
