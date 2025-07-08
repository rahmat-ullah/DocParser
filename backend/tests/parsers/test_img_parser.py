import pytest
import asyncio
from pathlib import Path
from PIL import Image

from app.parsers.img_parser import IMGParser

@pytest.fixture
def img_parser():
    return IMGParser()

@pytest.fixture
def image_file(tmp_path):
    # Create a simple PNG image
    img = Image.new('RGB', (100, 100), color='red')
    path = tmp_path / "test.png"
    img.save(str(path))
    return path

@pytest.mark.asyncio
async def test_img_parser_supports_file(img_parser, image_file):
    assert img_parser.supports_file(image_file) == True
    
@pytest.mark.asyncio
async def test_img_parser_parse(img_parser, image_file):
    result = await img_parser.parse_to_dict(image_file)
    assert isinstance(result, dict)
    assert "metadata" in result
    assert result["metadata"]["format"] == "IMAGE"
    assert result["metadata"]["image_format"] == "PNG"
    assert result["metadata"]["width"] == 100
    assert result["metadata"]["height"] == 100
    assert "images" in result
    assert len(result["images"]) == 1
    
    # Check image data
    image = result["images"][0]
    assert "data" in image
    assert "format" in image
    assert image["format"] == "PNG"
    assert len(image["data"]) > 0  # Base64 encoded data
