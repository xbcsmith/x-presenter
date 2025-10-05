#!/usr/bin/env python3
"""
Test script for the Markdown to PowerPoint converter.
"""

import sys
import os
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from presenter.converter import create_presentation


def test_converter():
    """Test the converter with the example slides."""
    input_file = "content/slides.md"
    output_file = "test_presentation.pptx"
    
    print(f"Converting {input_file} to {output_file}...")
    
    try:
        create_presentation(input_file, output_file)
        print("✅ Conversion successful!")
        print(f"📄 Output file: {output_file}")
        
        # Check if file was created
        if os.path.exists(output_file):
            file_size = os.path.getsize(output_file)
            print(f"📊 File size: {file_size:,} bytes")
        else:
            print("❌ Output file was not created")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ Error during conversion: {e}")
        return False


if __name__ == "__main__":
    success = test_converter()
    sys.exit(0 if success else 1)