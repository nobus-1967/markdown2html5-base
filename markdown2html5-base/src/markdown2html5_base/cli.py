import argparse
import sys

from markdown2html5_base import __version__
from markdown2html5_base.converter import MarkdownToHTML


def main() -> None:
    """Convert a Markdown file from the command line, optionally embedding CSS."""
    parser = argparse.ArgumentParser(
        description="Convert Markdown (basic and extended syntax) into valid HTML5."
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
        "--css",
        action="store_true",
        help="Embed the default viewing-friendly <style> block in <head>",
    )

    args = parser.parse_args()

    try:
        html_output = MarkdownToHTML().convert(args.input.read(), include_css=args.css)
        args.output.write(html_output)
        if html_output and not html_output.endswith("\n"):
            args.output.write("\n")
    except Exception as error:  # noqa: BLE001
        sys.stderr.write(f"Error: {error}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
