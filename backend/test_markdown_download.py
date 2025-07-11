"""
Test script for the markdown download endpoint.
"""

import asyncio
import aiohttp
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


async def test_markdown_download():
    """Test the markdown download endpoint."""
    base_url = "http://localhost:8000/api/v1"
    
    # Test document ID - you'll need to replace this with an actual document ID
    document_id = "test-document-id"
    
    async with aiohttp.ClientSession() as session:
        # Test 1: Download markdown endpoint
        print("Testing GET /documents/{id}/markdown endpoint...")
        try:
            async with session.get(f"{base_url}/documents/{document_id}/markdown") as response:
                print(f"Status: {response.status}")
                if response.status == 200:
                    # Check headers
                    content_disposition = response.headers.get('Content-Disposition', '')
                    print(f"Content-Disposition: {content_disposition}")
                    
                    # Save the file
                    content = await response.read()
                    with open(f"downloaded_{document_id}.md", "wb") as f:
                        f.write(content)
                    print(f"Downloaded markdown file: downloaded_{document_id}.md")
                else:
                    error = await response.json()
                    print(f"Error: {error}")
        except Exception as e:
            print(f"Error testing markdown download: {e}")
        
        # Test 2: Export endpoint with cached markdown
        print("\nTesting POST /export/{id} endpoint with cached markdown...")
        try:
            export_request = {
                "format": "markdown",
                "options": {
                    "cached": True
                }
            }
            async with session.post(
                f"{base_url}/export/{document_id}", 
                json=export_request
            ) as response:
                print(f"Status: {response.status}")
                if response.status == 200:
                    content_disposition = response.headers.get('Content-Disposition', '')
                    print(f"Content-Disposition: {content_disposition}")
                    print("Export with cached markdown successful")
                else:
                    error = await response.json()
                    print(f"Error: {error}")
        except Exception as e:
            print(f"Error testing export endpoint: {e}")
        
        # Test 3: Get available formats
        print("\nTesting GET /export/{id}/formats endpoint...")
        try:
            async with session.get(f"{base_url}/export/{document_id}/formats") as response:
                print(f"Status: {response.status}")
                if response.status == 200:
                    formats = await response.json()
                    print(f"Available formats: {formats}")
                else:
                    error = await response.json()
                    print(f"Error: {error}")
        except Exception as e:
            print(f"Error testing formats endpoint: {e}")


if __name__ == "__main__":
    print("Starting markdown download endpoint tests...")
    print("Make sure the server is running on localhost:8000")
    print("You'll need to replace the test document ID with a real one")
    print("-" * 50)
    asyncio.run(test_markdown_download())
