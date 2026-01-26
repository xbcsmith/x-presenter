"""
Command-line interface for the Markdown to PowerPoint converter.
"""

import argparse
import logging
import os
import sys

from .config import Config
from .converter import create_presentation


def debug_except_hook(type, value, tb):
    print("Godzilla hates {0}".format(type.__name__))
    print(str(type))
    import pdb
    import traceback

    traceback.print_exception(type, value, tb)
    pdb.post_mortem(tb)


debug = os.environ.get("PRESENTER_DEBUG", False)
level = logging.INFO
if debug:
    sys.excepthook = debug_except_hook
    level = logging.DEBUG
log_format = "%(asctime)s %(name)s:%(lineno)d:[%(levelname)s] %(message)s"
logging.basicConfig(stream=sys.stderr, level=level, format=log_format)
logger = logging.getLogger(__name__)


class CmdLine(object):
    """Command-line interface dispatcher for md2ppt.

    Uses dispatch pattern to route commands to appropriate methods.
    Currently supports 'create' command for markdown to PowerPoint conversion.
    """

    def __init__(self):
        """Initialize command-line parser and dispatch to appropriate subcommand.

        Parses first argument to determine subcommand, then invokes corresponding
        method. Supports 'create' subcommand for presentation generation.

        Raises:
            SystemExit: If unrecognized command provided
        """
        parser = argparse.ArgumentParser(
            description="Convert Markdown presentations to PowerPoint format",
            usage="""md2ppt <command> [<args>]

            md2ppt commands are:
                create      Convert Markdown file(s) to PowerPoint presentation
            """,
            epilog="""
                Examples:
                md2ppt create slides.md presentation.pptx
                md2ppt create testdata/content/slides.md output/presentation.pptx --verbose
                md2ppt create slides.md presentation.pptx --background background.jpg
                md2ppt create testdata/content/slides.md presentation.pptx -b testdata/content/background.jpg --verbose
                md2ppt create slides.md output.pptx --background-color 1E3A8A --font-color FFFFFF
                md2ppt create slides.md output.pptx --title-bg-color 0F172A --title-font-color F59E0B
            """,
        )

        parser.add_argument("command", help="Subcommand to run")
        # parse_args defaults to [1:] for args, but you need to
        # exclude the rest of the args too, or validation will fail
        args = parser.parse_args(sys.argv[1:2])
        if not hasattr(self, args.command):
            logger.error("Unrecognized command")
            parser.print_help()
            sys.exit(1)
        # use dispatch pattern to invoke method with same name
        getattr(self, args.command)()

    def create(self) -> int:
        """Create PowerPoint presentation from Markdown file(s).

        Parses command-line arguments and delegates to create_presentation()
        function. Supports three distinct usage modes:

        Mode 1 - Input/output pair:
            Single input file with explicit output filename.
            Usage: md2ppt create input.md output.pptx
            Creates: output.pptx with content from input.md

        Mode 2 - Single file with auto output:
            Single input file with auto-generated output name.
            Usage: md2ppt create input.md
            Creates: input.pptx in same directory as input.md

        Mode 3 - Multiple files with output directory:
            Multiple input files to specified output directory.
            Usage: md2ppt create a.md b.md c.md --output ./presentations/
            Creates: presentations/a.pptx, presentations/b.pptx, presentations/c.pptx

        Supported options:
            --output DIR: Output directory (Mode 3) or filename (Mode 1)
            --background FILE: Background image for all slides
            --background-color COLOR: Background color for content slides (hex: RRGGBB or #RRGGBB)
            --font-color COLOR: Font color for content slides (hex: RRGGBB or #RRGGBB)
            --title-bg-color COLOR: Background color for title slide (hex: RRGGBB or #RRGGBB)
            --title-font-color COLOR: Font color for title slide (hex: RRGGBB or #RRGGBB)
            --verbose: Enable verbose logging
            --debug: Enable debug mode

        Returns:
            int: Return code (0 on success)

        Raises:
            SystemExit: On argument parsing error or multiple files without --output
        """
        parser = argparse.ArgumentParser(description="Create PPT from Markdown\n")
        parser.add_argument(
            "--output",
            dest="output_path",
            action="store",
            default="",
            help="Directory for output files (multi-file mode) or output filename (single file mode)",
        )
        parser.add_argument(
            "--background",
            dest="background_path",
            action="store",
            default="",
            help="Path to background image file for all slides",
        )
        parser.add_argument(
            "--background-color",
            dest="background_color",
            action="store",
            default="",
            help="Background color for content slides (hex format: RRGGBB or #RRGGBB)",
        )
        parser.add_argument(
            "--font-color",
            dest="font_color",
            action="store",
            default="",
            help="Font color for content slides (hex format: RRGGBB or #RRGGBB)",
        )
        parser.add_argument(
            "--title-bg-color",
            dest="title_bg_color",
            action="store",
            default="",
            help="Background color for title slide (hex format: RRGGBB or #RRGGBB)",
        )
        parser.add_argument(
            "--title-font-color",
            dest="title_font_color",
            action="store",
            default="",
            help="Font color for title slide (hex format: RRGGBB or #RRGGBB)",
        )
        parser.add_argument(
            "--verbose",
            dest="verbose",
            action="store_true",
            default=False,
            help="enable verbose output",
        )
        parser.add_argument(
            "--debug",
            dest="debug",
            action="store_true",
            default=False,
            help="Turn debug on",
        )
        parser.add_argument(
            "filenames",
            nargs="+",
            action="store",
            default=None,
            help="Input markdown file(s) or input/output pair (input.md output.pptx)",
        )
        args = parser.parse_args(sys.argv[2:])
        info = vars(args)

        # Detect mode and normalize arguments
        filenames = info.pop("filenames")
        output_path = info.get("output_path", "")
        output_file = ""

        # Mode detection:
        # 1. Exactly 2 positional args + no --output = input/output pair
        # 2. 1+ args + --output specified = multi-file with output directory
        # 3. 1 arg + no --output = single file, auto-generate output
        # 4. 2+ args + no --output + no --output = error
        if len(filenames) == 2 and not output_path:
            # Mode 1: Input/output pair
            info["filenames"] = [filenames[0]]
            output_file = filenames[1]
            info["output_file"] = output_file
        elif len(filenames) >= 1 and output_path:
            # Mode 2: Multi-file with output directory
            info["filenames"] = filenames
            info["output_path"] = output_path
            info["output_file"] = ""
        elif len(filenames) == 1 and not output_path:
            # Mode 3: Single file, auto-generate output
            info["filenames"] = filenames
            info["output_path"] = ""
            info["output_file"] = ""
        elif len(filenames) > 1 and not output_path:
            # Mode 4: Error - ambiguous
            logger.error(
                "Multiple input files specified without --output directory. "
                "Use: md2ppt create file1.md file2.md --output ./dir/"
            )
            sys.exit(1)
        else:
            # Fallback
            info["filenames"] = filenames
            info["output_file"] = ""

        # deepcode ignore PT: <please specify a reason of ignoring this>
        cfg = Config(**info)
        return create_presentation(cfg)


def main() -> int:
    """Entry point for md2ppt command-line application.

    Initializes command-line interface and processes user commands.
    Handles both 'create' command for presentation generation.

    Returns:
        int: Return code (0 on success, non-zero on error)

    Examples:
        >>> # Run via command line:
        >>> # md2ppt create slides.md output.pptx
        >>> # md2ppt create slides.md --background bg.jpg --verbose
    """
    try:
        CmdLine()
        return 0
    except SystemExit as e:
        return e.code if isinstance(e.code, int) else 1
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
