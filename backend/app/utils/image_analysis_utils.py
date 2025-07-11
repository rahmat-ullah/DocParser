import pytesseract
from PIL import Image
import openai
from typing import Optional

from backend.app.parsers.ast_models import TableBlock
from backend.app.utils.markdown_utils import parse_markdown_table_to_table_block
from backend.app.core.config import settings # For API key and model

async def extract_table_from_pil_image(
    image_pil: Image.Image,
    image_name: str = "image"
) -> Optional[TableBlock]:
    """
    Extracts a table from a PIL Image object using OCR and LLM.

    Args:
        image_pil: The PIL Image object to process.
        image_name: An optional name/identifier for the image (used in prompts/captions).

    Returns:
        A TableBlock object if a table is found, otherwise None.
    """
    if not image_pil:
        return None

    # Ensure OpenAI API key is set (it should be set globally by application startup,
    # but this is a safeguard or place for more specific error handling if needed)
    if not settings.OPENAI_API_KEY:
        print(f"Warning: OPENAI_API_KEY not set. Skipping table extraction for {image_name}.")
        # In a real app, might raise an error or log more formally
        return None

    # Set API key for the current context if not already set by openai client's initialization
    # This might be redundant if openai client is configured once globally.
    if not openai.api_key and settings.OPENAI_API_KEY:
        openai.api_key = settings.OPENAI_API_KEY


    try:
        raw_text = pytesseract.image_to_string(image_pil)

        if not raw_text.strip():
            return None # No text detected

        prompt = f"""The following text was extracted from an image named '{image_name}'.
Please identify if there is a table in this text.
If a table is found, format it as a Markdown table.
If no table is found, respond with "No table found".

Raw text:
---
{raw_text}
---
Markdown table:
"""
        # Ensure openai.api_key is effectively set before this call
        if not openai.api_key: # Double check, as it's critical
             print(f"Error: OpenAI API key is not available for LLM call for {image_name}.")
             return None

        response = await openai.chat.completions.create(
            model=settings.OPENAI_MODEL or "gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that extracts tables from text and formats them in Markdown."},
                {"role": "user", "content": prompt}
            ],
            timeout=settings.OPENAI_TIMEOUT # Use configured timeout
        )

        markdown_table_str = response.choices[0].message.content.strip()

        if markdown_table_str.lower() == "no table found" or not markdown_table_str:
            return None

        table_block = parse_markdown_table_to_table_block(
            markdown_table_str,
            caption=f"Table from {image_name}"
        )
        return table_block

    except pytesseract.TesseractNotFoundError:
        print("Error: Tesseract is not installed or not in your PATH. Skipping table extraction.")
        # Log this error appropriately in a real application
        return None
    except openai.APIError as e:
        print(f"OpenAI API Error during table extraction for {image_name}: {e}. Skipping.")
        # Log this error
        return None
    except Exception as e:
        print(f"An unexpected error occurred during table extraction for {image_name}: {e}")
        # Log this error
        return None
