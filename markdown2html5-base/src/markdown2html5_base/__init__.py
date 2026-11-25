"""Convert Markdown text into clean, modern and print-ready HTML5 markup."""

from .converter import (
    DEFAULT_PAGE_LAYOUT,
    PAGE_LAYOUTS,
    MarkdownToHTML,
)

__all__ = ["DEFAULT_PAGE_LAYOUT", "PAGE_LAYOUTS", "MarkdownToHTML"]
__version__ = "1.0.0"
