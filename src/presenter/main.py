"""
Command-line interface for the Markdown to PowerPoint converter.
"""

import argparse
import os
import sys
from pathlib import Path
from .converter import create_presentation


def main() -> None:
    """
    Convert Markdown presentation to PowerPoint format.
    """
    parser = argparse.ArgumentParser(
        description="Convert Markdown presentation to PowerPoint format",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  md2ppt slides.md presentation.pptx
  md2ppt content/slides.md output/presentation.pptx --verbose
  md2ppt slides.md presentation.pptx --background background.jpg
  md2ppt content/slides.md presentation.pptx -b content/background.jpg --verbose
        """
    )
    
    parser.add_argument(
        'input_file',
        type=str,
        help='Path to the Markdown file containing slides separated by "---"'
    )
    
    parser.add_argument(
        'output_file',
        type=str,
        help='Path where the PowerPoint presentation will be saved'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose output'
    )
    
    parser.add_argument(
        '--background', '-b',
        type=str,
        help='Path to background image file for all slides'
    )
    
    args = parser.parse_args()
    
    # Convert to Path objects
    input_file = Path(args.input_file)
    output_file = Path(args.output_file)
    
    # Check if input file exists
    if not input_file.exists():
        print(f"❌ Error: Input file '{input_file}' does not exist", file=sys.stderr)
        sys.exit(1)
    
    if args.verbose:
        print(f"Converting {input_file} to {output_file}")
    
    # Ensure output directory exists
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Add .pptx extension if not present
    if not output_file.suffix:
        output_file = output_file.with_suffix('.pptx')
    elif output_file.suffix.lower() not in ['.pptx', '.ppt']:
        output_file = output_file.with_suffix('.pptx')
    
    try:
        create_presentation(str(input_file), str(output_file), args.background)
        print(f"✅ Successfully created presentation: {output_file}")
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()