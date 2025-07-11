import re
import json

def extract_valid_json_from_response(response_text):
    """
    Extracts valid JSON content wrapped in triple backticks from the response text.
    """
    # Use regex to find text between ```json and ```
    json_blocks = re.findall(r'```json\s*(\{.*?\})\s*```', response_text, re.DOTALL)
    
    # Attempt to parse each JSON block
    for block in json_blocks:
        try:
            # Load the JSON to validate
            parsed_json = json.loads(block.strip())
            return parsed_json
        except json.JSONDecodeError as e:
            print(f"Invalid JSON in block: {e}")
    
    # Return None if no valid JSON was found
    return None

# Example usage
response = """
Here is the image analysis result:
```json
{
  "id": "fig-002",
  "type": "diagram",
  "title": "Network Diagram",
  "caption": "Figure shows network layout.",
  "source": {
    "filename": "network_report.pdf",
    "page": 5,
    "documentSection": "Chapter 2: Network Layout"
  }
}
```
More analysis can be found...
```json
{
  "id": "fig-003",
  "type": "chart",
  "title": "Data Chart",
  "caption": "Monthly sales data.",
  "source": {
    "filename": "sales_data.pdf",
    "page": 8,
    "documentSection": "Appendix A"
  }
}
```
"""

valid_json = extract_valid_json_from_response(response)
if valid_json:
    print("Extracted JSON:", valid_json)
else:
    print("No valid JSON found")

