"""Command-line interface converting a Markdown file into a styled HTML5 document."""

import argparse
import sys

from markdown2html5_base import __version__
from markdown2html5_base.converter import (
    DEFAULT_PAGE_LAYOUT,
    PAGE_LAYOUTS,
    MarkdownToHTML,
)


def main() -> None:
    """Convert a Markdown file from the command line with print-ready CSS."""
    parser = argparse.ArgumentParser(
        description="Convert Markdown (basic and extended syntax) into styled HTML5."
    )
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
        help="Show the library version and exit",
    )
    parser.add_argument(
        "input",
        nargs="?",
        type=argparse.FileType("r", encoding="utf-8"),
        default=sys.stdin,
        help="Input Markdown file (defaults to stdin if not specified)",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=argparse.FileType("w", encoding="utf-8"),
        default=sys.stdout,
        help="Output HTML5 file (defaults to stdout if not specified)",
    )
    parser.add_argument(
        "--page",
        dest="page",
        metavar="LAYOUT",
        choices=PAGE_LAYOUTS,
        default=DEFAULT_PAGE_LAYOUT,
        help=f"Page orientation: portrait or landscape (default: {DEFAULT_PAGE_LAYOUT})",
    )
    parser.add_argument(
        "--orientation",
        dest="page",
        metavar="LAYOUT",
        choices=PAGE_LAYOUTS,
        default=argparse.SUPPRESS,
        help=argparse.SUPPRESS,
    )

    args = parser.parse_args()

    try:
        html_output = MarkdownToHTML().convert(args.input.read(), orientation=args.page)
        args.output.write(html_output)
        if html_output and not html_output.endswith("\n"):
            args.output.write("\n")
    except Exception as error:  # noqa: BLE001
        sys.stderr.write(f"Error: {error}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
