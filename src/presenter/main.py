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
    def __init__(self):
        parser = argparse.ArgumentParser(
            description="Pipeline Third Party Notice Tools",
            usage="""md2ppt <command> [<args>]

            md2ppt commands are:
                create      create TPN report from SBOMs
            """,
            epilog="""
                Examples:
                md2ppt create slides.md presentation.pptx
                md2ppt create testdata/content/slides.md output/presentation.pptx --verbose
                md2ppt create slides.md presentation.pptx --background background.jpg
                md2ppt create testdata/content/slides.md presentation.pptx -b testdata/content/background.jpg --verbose
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

    def create(self):
        """
        create PPT from Markdown
        """
        parser = argparse.ArgumentParser(description="Create PPT from Markdown\n")
        parser.add_argument(
            "--output",
            dest="output_path",
            action="store_true",
            default=False,
            help="Directory to write ppt to",
        )
        parser.add_argument(
            "--background",
            dest="background_path",
            action="store",
            default="",
            help="Path to background image file for all slides",
        )
        parser.add_argument(
            "--verbose",
            dest="verbose",
            action="store_true",
            default=False,
            description="enable verbose output",
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
            help='Path to the Markdown file containing slides separated by"---"',
        )
        args = parser.parse_args(sys.argv[2:])
        info = vars(args)
        # deepcode ignore PT: <please specify a reason of ignoring this>
        cfg = Config(**info)
        return create_presentation(cfg)


def main():
    CmdLine()


if __name__ == "__main__":
    sys.exit(main())
