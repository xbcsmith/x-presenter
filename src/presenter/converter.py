"""
Core module for converting Markdown presentations to PowerPoint.
"""

import os
import re
from typing import Any, Dict, List, Optional

from pptx import Presentation
from pptx.enum.text import MSO_AUTO_SIZE
from pptx.util import Inches, Pt


class MarkdownToPowerPoint:
    """Convert Markdown presentations to PowerPoint format."""

    def __init__(self, background_image: Optional[str] = None):
        """Initialize the converter.

        Args:
            background_image: Path to background image file (optional)
        """
        self.presentation = Presentation()
        self.slide_separator = "---"
        self.background_image = background_image

    def parse_markdown_slides(self, markdown_content: str) -> List[str]:
        """
        Parse markdown content into individual slides using '---' separator.

        Args:
            markdown_content: Raw markdown text

        Returns:
            List of slide content strings
        """
        # Split content by slide separator
        slides = markdown_content.split(self.slide_separator)

        # Clean up each slide (remove extra whitespace)
        cleaned_slides = []
        for slide in slides:
            slide_content = slide.strip()
            if slide_content:  # Only include non-empty slides
                cleaned_slides.append(slide_content)

        return cleaned_slides

    def parse_slide_content(self, slide_markdown: str) -> Dict[str, Any]:
        """
        Parse individual slide content into structured data.

        Args:
            slide_markdown: Markdown content for a single slide

        Returns:
            Dictionary with parsed slide elements
        """
        lines = slide_markdown.strip().split("\n")
        slide_data = {"title": "", "content": [], "images": [], "lists": []}

        current_list = []
        in_list = False

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Check for title (# or ##)
            if line.startswith("# "):
                slide_data["title"] = line[2:].strip()
            elif line.startswith("## "):
                slide_data["title"] = line[3:].strip()

            # Check for images
            elif line.startswith("!["):
                image_match = re.match(r"!\[([^\]]*)\]\(([^)]+)\)", line)
                if image_match:
                    alt_text = image_match.group(1)
                    image_path = image_match.group(2)
                    slide_data["images"].append({"alt": alt_text, "path": image_path})

            # Check for list items
            elif line.startswith("- ") or line.startswith("* "):
                if not in_list:
                    in_list = True
                    current_list = []
                current_list.append(line[2:].strip())

            # Regular content
            else:
                if in_list and current_list:
                    slide_data["lists"].append(current_list)
                    current_list = []
                    in_list = False

                if not line.startswith("#") and line:
                    slide_data["content"].append(line)

        # Don't forget the last list if we ended with one
        if in_list and current_list:
            slide_data["lists"].append(current_list)

        return slide_data

    def add_slide_to_presentation(
        self, slide_data: Dict[str, Any], base_path: str = ""
    ):
        """
        Add a slide to the presentation based on parsed data.

        Args:
            slide_data: Parsed slide data
            base_path: Base path for resolving relative image paths
        """
        # Use blank slide layout
        slide_layout = self.presentation.slide_layouts[6]  # Blank layout
        slide = self.presentation.slides.add_slide(slide_layout)

        # Add background image if specified (add it first so other content appears on top)
        if self.background_image and os.path.exists(self.background_image):
            try:
                # Add background image to cover the entire slide
                slide.shapes.add_picture(
                    self.background_image,
                    Inches(0),  # Left position
                    Inches(0),  # Top position
                    width=Inches(10),  # Standard slide width
                    height=Inches(7.5),  # Standard slide height
                )
            except Exception as e:
                print(
                    f"Warning: Could not add background image {self.background_image}: {e}"
                )
        elif self.background_image:
            print(f"Warning: Background image not found: {self.background_image}")

        # Track vertical position for content placement
        top_position = Inches(0.5)

        # Add title if present
        if slide_data["title"]:
            title_box = slide.shapes.add_textbox(
                Inches(0.5), top_position, Inches(9), Inches(1)
            )
            title_frame = title_box.text_frame
            title_frame.text = slide_data["title"]

            # Format title
            title_paragraph = title_frame.paragraphs[0]
            title_paragraph.font.size = Pt(32)
            title_paragraph.font.bold = True

            top_position = Inches(top_position.inches + 1.2)

        # Add regular content
        if slide_data["content"]:
            content_text = "\n".join(slide_data["content"])
            if content_text.strip():
                content_box = slide.shapes.add_textbox(
                    Inches(0.5), top_position, Inches(9), Inches(2)
                )
                content_frame = content_box.text_frame
                content_frame.text = content_text
                content_frame.word_wrap = True
                content_frame.auto_size = MSO_AUTO_SIZE.SHAPE_TO_FIT_TEXT

                # Format content
                for paragraph in content_frame.paragraphs:
                    paragraph.font.size = Pt(18)

                top_position = Inches(top_position.inches + 2.5)

        # Add lists
        for list_items in slide_data["lists"]:
            list_height = len(list_items) * 0.4
            list_box = slide.shapes.add_textbox(
                Inches(1), top_position, Inches(8), Inches(list_height)
            )
            list_frame = list_box.text_frame
            list_frame.clear()

            for i, item in enumerate(list_items):
                if i == 0:
                    # First item uses the existing paragraph
                    p = list_frame.paragraphs[0]
                else:
                    # Add new paragraphs for subsequent items
                    p = list_frame.add_paragraph()

                p.text = f"• {item}"
                p.font.size = Pt(16)
                p.level = 0

            top_position = Inches(top_position.inches + list_height + 0.3)

        # Add images
        for image_info in slide_data["images"]:
            image_path = image_info["path"]

            # Handle relative paths
            if not os.path.isabs(image_path):
                if image_path.startswith("./"):
                    image_path = image_path[2:]
                image_path = os.path.join(base_path, image_path)

            if os.path.exists(image_path):
                try:
                    # Add image to slide
                    slide.shapes.add_picture(
                        image_path, Inches(2), top_position, height=Inches(3)
                    )
                    top_position = Inches(top_position.inches + 3.5)
                except Exception as e:
                    print(f"Warning: Could not add image {image_path}: {e}")
            else:
                print(f"Warning: Image not found: {image_path}")

    def convert(
        self,
        markdown_file: str,
        output_file: str,
        background_image: Optional[str] = None,
    ) -> None:
        """
        Convert a markdown file to PowerPoint presentation.

        Args:
            markdown_file: Path to input markdown file
            output_file: Path to output PowerPoint file
            background_image: Path to background image file (optional)
        """
        # Set background image if provided
        if background_image:
            # Handle relative paths - resolve relative to current working directory, not markdown file
            if not os.path.isabs(background_image):
                background_image = os.path.abspath(background_image)
            self.background_image = background_image

        # Read markdown content
        with open(markdown_file, "r", encoding="utf-8") as f:
            markdown_content = f.read()

        # Parse slides
        slides_content = self.parse_markdown_slides(markdown_content)

        if not slides_content:
            raise ValueError("No slides found in markdown content")

        # Get base path for resolving relative image paths
        base_path = os.path.dirname(os.path.abspath(markdown_file))

        # Process each slide
        for slide_content in slides_content:
            slide_data = self.parse_slide_content(slide_content)
            self.add_slide_to_presentation(slide_data, base_path)

        # Save presentation
        self.presentation.save(output_file)
        print(f"Presentation saved to: {output_file}")


def create_presentation(cfg) -> None:
    """
    Convenience function to create a PowerPoint presentation from markdown.

    Args:
        markdown_file: Path to input markdown file
        output_file: Path to output PowerPoint file
        background_image: Path to background image file (optional)
    """
    for filename in cfg.filenames:
        base_name = os.path.splitext(filename)[0]
        base_name_only = os.path.basename(base_name)
        output_filename = base_name_only + ".pptx"
        if cfg.output_path:
            output_file = os.path.join(cfg.output_path, output_filename)
        else:
            output_file = base_name + ".pptx"
        background_image = None
        if os.path.exists(cfg.background_path):
            background_image = cfg.background_path
        converter = MarkdownToPowerPoint(background_image)
        converter.convert(filename, output_file, background_image)
    return 0
