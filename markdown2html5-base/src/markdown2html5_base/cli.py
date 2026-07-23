import sys
import argparse
from markdown2html5_base.converter import MarkdownToHTML

def main():
    parser = argparse.ArgumentParser(
        description="Convert Markdown (basic and extended syntax) into valid HTML5."
    )
    parser.add_argument(
        "input", 
        nargs="?", 
        type=argparse.FileType("r", encoding="utf-8"), 
        default=sys.stdin,
        help="Input Markdown file (defaults to stdin if not specified)"
    )
    parser.add_argument(
        "-o", "--output", 
        type=argparse.FileType("w", encoding="utf-8"), 
        default=sys.stdout,
        help="Output HTML5 file (defaults to stdout if not specified)"
    )

    args = parser.parse_args()

    try:
        markdown_text = args.input.read()
        converter = MarkdownToHTML()
        html_output = converter.convert(markdown_text)
        args.output.write(html_output)
        
        # Ensure a final trailing newline for clean console/file output
        if html_output and not html_output.endswith('\n'):
            args.output.write('\n')
            
    except Exception as e:
        sys.stderr.write(f"Error: {str(e)}\n")
        sys.exit(1)

if __name__ == "__main__":
    main()
