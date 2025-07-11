from table_extractor import extract_table_from_image
import os

def run_test():
    """
    Tests the table extraction functionality using a sample image.
    """
    image_path = "sample_table_image.png" # Ensure this image is in the same directory

    if not os.path.exists(image_path):
        print(f"Test image not found at {image_path}. Please make sure it exists.")
        return

    print(f"Attempting to extract table from: {image_path}")

    # Check if OPENAI_API_KEY is set
    if not os.getenv("OPENAI_API_KEY"):
        print("Error: The OPENAI_API_KEY environment variable is not set.")
        print("Please create a .env file in the root directory with your OpenAI API key:")
        print("OPENAI_API_KEY='your_api_key_here'")
        print("\nSkipping table extraction test.")
        return

    markdown_table = extract_table_from_image(image_path)

    if markdown_table:
        print("\nSuccessfully extracted table in Markdown format:\n")
        print(markdown_table)
    else:
        print("\nNo table was extracted, or an error occurred during the process.")
        print("Please check the console output from table_extractor.py for more details.")

if __name__ == "__main__":
    print("Running table extraction test...")
    print("Make sure you have created a .env file with your OPENAI_API_KEY.")
    print("Example .env file content: OPENAI_API_KEY='your_actual_api_key'")
    print("-" * 30)
    run_test()
