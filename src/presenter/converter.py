"""
Core module for converting Markdown presentations to PowerPoint.
"""

import logging
import os
import re
from typing import TYPE_CHECKING, Any, Dict, List, Optional

from pptx import Presentation
from pptx.enum.text import MSO_AUTO_SIZE
from pptx.util import Inches, Pt

if TYPE_CHECKING:
    from .config import Config

logger = logging.getLogger(__name__)


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
        """Parse markdown content into individual slides using '---' separator.

        Splits markdown content by '---' separator and returns list of cleaned
        slide content. Empty slides are filtered out. Whitespace is normalized.

        Args:
            markdown_content: Raw markdown text containing one or more slides
                separated by '---' on its own line

        Returns:
            List[str]: List of cleaned slide content strings, in order.
                Each slide is stripped of leading/trailing whitespace.
                Empty slides are excluded from result.

        Raises:
            No exceptions raised - returns empty list if no valid slides found

        Examples:
            >>> converter = MarkdownToPowerPoint()
            >>> content = "# Slide 1\\n---\\n# Slide 2"
            >>> slides = converter.parse_markdown_slides(content)
            >>> len(slides)
            2
            >>> slides[0]
            '# Slide 1'
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
        """Parse individual slide content into structured data.

        Extracts and structures markdown elements from a single slide including
        titles, lists, regular text content, and image references. Handles both
        '-' and '*' style bullet points.

        Args:
            slide_markdown: Markdown content for a single slide

        Returns:
            Dict[str, Any]: Dictionary with keys:
                'title' (str): Slide title from # or ## heading
                'content' (List[str]): Regular text content lines
                'lists' (List[List[str]]): List items grouped by lists
                'images' (List[Dict]): Image references with 'alt' and 'path'

        Examples:
            >>> converter = MarkdownToPowerPoint()
            >>> content = "# Title\\n- Item 1\\n- Item 2"
            >>> data = converter.parse_slide_content(content)
            >>> data['title']
            'Title'
            >>> len(data['lists'])
            1
            >>> data['lists'][0]
            ['Item 1', 'Item 2']
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
    ) -> None:
        """Add a slide to the presentation based on parsed data.

        Creates a new slide with parsed content including title, text content,
        bullet lists, and images. Handles background images if configured.
        Automatically positions content vertically on the slide.

        Args:
            slide_data: Parsed slide data dictionary with keys:
                'title': Slide title text (str)
                'content': Regular text content lines (List[str])
                'lists': Bullet lists grouped (List[List[str]])
                'images': Image references with alt text (List[Dict])
            base_path: Base directory path for resolving relative image paths.
                Used to resolve ./image.png style references.

        Returns:
            None

        Side Effects:
            Adds a new slide to self.presentation with all parsed content.
            Modifies presentation state by adding shapes (text boxes, images).

        Examples:
            >>> converter = MarkdownToPowerPoint()
            >>> slide_data = {
            ...     'title': 'My Slide',
            ...     'content': ['Some text'],
            ...     'lists': [['Item 1', 'Item 2']],
            ...     'images': []
            ... }
            >>> converter.add_slide_to_presentation(slide_data)
            >>> len(converter.presentation.slides) == 1
            True
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
        """Convert a markdown file to PowerPoint presentation.

        Reads markdown content from input file, parses slides separated by '---',
        and generates a PowerPoint presentation with support for titles, lists,
        content, and optional background images.

        Args:
            markdown_file: Path to input markdown file to convert
            output_file: Path where output .pptx file will be saved
            background_image: Optional path to background image file for all slides.
                If provided and file exists, image will be added as background to
                each slide.

        Returns:
            None

        Raises:
            FileNotFoundError: If markdown_file cannot be read
            ValueError: If markdown content is empty or contains no valid slides
            IOError: If output file cannot be written

        Examples:
            >>> converter = MarkdownToPowerPoint()
            >>> converter.convert('slides.md', 'output.pptx')
            Presentation saved to: output.pptx

            >>> converter = MarkdownToPowerPoint(background_image='bg.jpg')
            >>> converter.convert('slides.md', 'output.pptx')
            Presentation saved to: output.pptx
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


def create_presentation(cfg: Config) -> int:
    """Create a PowerPoint presentation from one or more markdown files.

    Supports three distinct usage modes for flexible file handling:

    Mode 1 - Input/output pair:
        Single input file with explicit output filename.
        Example: md2ppt create input.md output.pptx
        Creates: output.pptx in current directory

    Mode 2 - Single file, auto output:
        Single input file with auto-generated output name.
        Example: md2ppt create input.md
        Creates: input.pptx in same directory as input.md

    Mode 3 - Multiple files with output directory:
        Multiple input files processed to specified output directory.
        Example: md2ppt create a.md b.md --output ./presentations/
        Creates: presentations/a.pptx, presentations/b.pptx

    Args:
        cfg: Config dataclass instance containing configuration parameters:
            filenames (List[str]): List of input markdown file paths to process
            output_path (str): Output directory path for multi-file mode (Mode 3).
                Empty string for single-file modes.
            output_file (str): Explicit output filename for Mode 1.
                Empty string for Modes 2 and 3.
            background_path (str): Optional path to background image file.
                Will be added to all slides if file exists.
            verbose (bool): Enable verbose logging output
            debug (bool): Enable debug mode with detailed output

    Returns:
        int: Return code (0 on success)

    Raises:
        FileNotFoundError: If any input markdown file does not exist
        ValueError: If markdown content is empty or contains no valid slides
        IOError: If output file or directory cannot be created or written

    Examples:
        >>> from presenter.config import Config
        >>> from presenter.converter import create_presentation
        >>> cfg = Config(filenames=['slides.md'], output_file='output.pptx')
        >>> create_presentation(cfg)
        Presentation saved to: output.pptx
        0

        >>> cfg = Config(
        ...     filenames=['deck1.md', 'deck2.md'],
        ...     output_path='./presentations/',
        ...     background_path='template.jpg'
        ... )
        >>> create_presentation(cfg)
        Presentation saved to: presentations/deck1.pptx
        Presentation saved to: presentations/deck2.pptx
        0
    """
    # Validate input files exist
    for filename in cfg.filenames:
        if not os.path.exists(filename):
            logger.error(f"Input file not found: {filename}")
            raise FileNotFoundError(f"Input file not found: {filename}")

    # Create output directory if specified and doesn't exist
    if cfg.output_path and not os.path.exists(cfg.output_path):
        os.makedirs(cfg.output_path, exist_ok=True)
        if cfg.verbose:
            logger.info(f"Created output directory: {cfg.output_path}")

    # Prepare background image (validate once for all files)
    background_image = None
    if cfg.background_path:
        if os.path.exists(cfg.background_path):
            background_image = cfg.background_path
            if cfg.verbose:
                logger.info(f"Using background image: {background_image}")
        else:
            logger.warning(f"Background image not found: {cfg.background_path}")

    # Process each input file
    for filename in cfg.filenames:
        # Determine output filename based on mode
        if cfg.output_file:
            # Mode 1: Input/output pair - use explicit output filename
            output_file = cfg.output_file
            if cfg.verbose:
                logger.info(f"Converting {filename} -> {output_file}")
        elif cfg.output_path:
            # Mode 2: Multiple files with output directory
            base_name_only = os.path.basename(os.path.splitext(filename)[0])
            output_filename = base_name_only + ".pptx"
            output_file = os.path.join(cfg.output_path, output_filename)
            if cfg.verbose:
                logger.info(f"Converting {filename} -> {output_file}")
        else:
            # Mode 3: Single file, auto-generate output in same directory
            base_name = os.path.splitext(filename)[0]
            output_file = base_name + ".pptx"
            if cfg.verbose:
                logger.info(f"Converting {filename} -> {output_file}")

        # Create converter and process file
        converter = MarkdownToPowerPoint(background_image)
        converter.convert(filename, output_file, background_image)

    return 0
