"""Convert Markdown documents into clean, modern HTML5 markup.

The converter walks the source line by line, resolving block structures
(front matter, headings, lists, tables, blockquotes, footnotes) and then
applies the inline rules to the text of each block.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import ClassVar, Pattern

PAGE_LAYOUTS = ("portrait", "landscape")
DEFAULT_PAGE_LAYOUT = "portrait"


@dataclass
class _ListFrame:
    """State of one open <ul>/<ol> level during conversion."""

    tag: str
    indent: int
    li_pending: bool


class MarkdownToHTML:
    """A high-performance parser to convert custom Markdown documents to HTML."""

    EMOJIS: ClassVar[dict[str, str]] = {
        "joy": "😂",
        "smile": "😄",
        "heart": "❤️",
        "thumbsup": "👍",
        "thumbsdown": "👎",
        "wink": "😉",
        "tada": "🎉",
        "rocket": "🚀",
        "fire": "🔥",
        "star": "⭐",
        "cry": "😢",
        "thinking": "🤔",
        "100": "💯",
        "sparkles": "✨",
        "eyes": "👀",
        "bulb": "💡",
        "warning": "⚠️",
        "ok": "👌",
        "check_mark": "✔️",
    }

    ESCAPE_CHARS: ClassVar[dict[str, str]] = {
        "\\": "%%ESCBACKSLASH%%",
        "`": "%%ESCBACKTICK%%",
        "*": "%%ESCASTERISK%%",
        "_": "%%ESCUNDERSCORE%%",
        "{": "%%ESCLBRACE%%",
        "}": "%%ESCRBRACE%%",
        "[": "%%ESCLBRACKET%%",
        "]": "%%ESCRBRACKET%%",
        "(": "%%ESCLPAREN%%",
        ")": "%%ESCRPAREN%%",
        "#": "%%ESCHASH%%",
        "+": "%%ESCPLUS%%",
        "-": "%%ESCMINUS%%",
        ".": "%%ESCDOT%%",
        "/": "%%ESCSLASH%%",
        "!": "%%ESCEXCLAMATION%%",
        "|": "%%ESCPIPE%%",
        "~": "%%ESCTILDE%%",
        "^": "%%ESCCARET%%",
        "=": "%%ESCEQUAL%%",
        ":": "%%ESCCOLON%%",
        "<": "%%ESCLT%%",
        ">": "%%ESCGT%%",
    }

    RESTORED_ESCAPES: ClassVar[dict[str, str]] = {
        "<": "&lt;",
        ">": "&gt;",
    }

    # The `_` rules use CommonMark's intraword rule: an underscore only opens
    # emphasis when it is not glued to a word on its left, and only closes it
    # when it is not glued to a word on its right.  That keeps identifiers such
    # as `snake_case_name` and URLs such as `a_b_c` intact, while `_italic_`
    # still works.  `*` emphasis is left unrestricted, as in CommonMark.
    INLINE_RULES: ClassVar[list[tuple[Pattern[str], str]]] = [
        (re.compile(r"\*\*\*(.*?)\*\*\*"), r"<strong><em>\1</em></strong>"),
        (
            re.compile(r"(?<![\w\\])___(?=\S)(.+?)(?<=\S)___(?!\w)"),
            r"<strong><em>\1</em></strong>",
        ),
        (re.compile(r"\*\*(.*?)\*\*"), r"<strong>\1</strong>"),
        (
            re.compile(r"(?<![\w\\])__(?=\S)(.+?)(?<=\S)__(?!\w)"),
            r"<strong>\1</strong>",
        ),
        (re.compile(r"\*(.*?)\*"), r"<em>\1</em>"),
        (re.compile(r"(?<![\w\\])_(?=\S)(.+?)(?<=\S)_(?!\w)"), r"<em>\1</em>"),
        (re.compile(r"~~(.*?)~~"), r"<s>\1</s>"),
        (re.compile(r"==(.*?)=="), r"<mark>\1</mark>"),
        (re.compile(r"\~(.*?)\~"), r"<sub>\1</sub>"),
        (re.compile(r"\^\^\^(.*?)\^\^\^"), r"<u><em>\1</em></u>"),
        (re.compile(r"\^\^(.*?)\^\^"), r"<u>\1</u>"),
        (re.compile(r"\^(.*?)\^"), r"<sup>\1</sup>"),
    ]

    TYPOGRAPHY_RULES: ClassVar[list[tuple[Pattern[str], str]]] = [
        (re.compile(r"\([cC]\)"), "&copy;"),
        (re.compile(r"\([tT][mM]\)"), "&trade;"),
        (re.compile(r"\([rR]\)"), "&reg;"),
        (re.compile(r"\+/-"), "&plusmn;"),
        (re.compile(r"!="), "&ne;"),
        (re.compile(r"<=>"), "&hArr;"),
        (re.compile(r"<="), "&le;"),
        (re.compile(r">="), "&ge;"),
        (re.compile(r"->"), "&rarr;"),
        (re.compile(r"<-"), "&larr;"),
        (re.compile(r"&uarr;"), "&uarr;"),
        (re.compile(r"&darr;"), "&darr;"),
        (re.compile(r"=>"), "&rArr;"),
        (re.compile(r"1/2"), "&frac12;"),
        (re.compile(r"1/3"), "&frac13;"),
        (re.compile(r"2/3"), "&frac23;"),
        (re.compile(r"1/4"), "&frac14;"),
        (re.compile(r"3/4"), "&frac34;"),
        (re.compile(r"&sol;"), "&sol;"),
        (re.compile(r"&bsol;"), "&bsol;"),
        (re.compile(r"<<"), "&laquo;"),
        (re.compile(r">>"), "&raquo;"),
        (re.compile(r"&ldquo;"), "&ldquo;"),
        (re.compile(r"&rdquo;"), "&rdquo;"),
        (re.compile(r'"([^"\n]+)"'), r"&ldquo;\1&rdquo;"),
        (re.compile(r"'([^'\n]+)'"), r"&lsquo;\1&rsquo;"),
        (re.compile(r"'"), "&apos;"),
        (re.compile(r"---"), "&mdash;"),
        (re.compile(r"--"), "&ndash;"),
        (re.compile(r"\.\.\."), "&hellip;"),
        (re.compile(r"&nbsp;"), "&nbsp;"),
    ]

    FOOTNOTE_REF_RE: ClassVar[Pattern[str]] = re.compile(r"\[\^([^\]\s]+)\]")
    FOOTNOTE_REF_HTML: ClassVar[str] = (
        r'<sup id="fnref:\1"><a href="#fn:\1" class="footnote-ref">\1</a></sup>'
    )

    BLOCK_LANG_RE: ClassVar[Pattern[str]] = re.compile(
        r"^\s*\{:([a-zA-Z0-9-]+)\}\s+(.*)$"
    )
    INLINE_LANG_RE: ClassVar[Pattern[str]] = re.compile(
        r"\{:([a-zA-Z0-9-]+)\}(.*?)\{:}"
    )
    IMAGE_RE: ClassVar[Pattern[str]] = re.compile(
        r"!\[([^\]]*)\]\((.*?)(?:\s+[\"']([^\"']*)[\"'])?\)"
    )
    EMOJI_RE: ClassVar[Pattern[str]] = re.compile(r":([a-zA-Z0-9_]+):")
    COMMENT_RE: ClassVar[Pattern[str]] = re.compile(r"^\[(.+)\]:\s+#\s*$")
    HEADING_RE: ClassVar[Pattern[str]] = re.compile(r"^(#{1,6})\s+(.*?)$")
    HEADING_ID_STRIP_RE: ClassVar[Pattern[str]] = re.compile(r"`+|\{:[^}]*\}|[*_~]")
    HEADING_SLUG_RE: ClassVar[Pattern[str]] = re.compile(r"[^\w\s-]+", re.UNICODE)
    HR_RE: ClassVar[Pattern[str]] = re.compile(r"^(?:-{3,}|\*{3,}|_{3,})$")
    RUBY_RE: ClassVar[Pattern[str]] = re.compile(r"\{([^{}:|]+)\|([^}]+)\}")
    PROTECT_CODE_RE: ClassVar[Pattern[str]] = re.compile(r"`([^`\n]+)`")
    FOOTNOTE_DEF_RE: ClassVar[Pattern[str]] = re.compile(r"^\[\^([^\]\s]+)\]:\s+(.*?)$")

    FRONT_MATTER_KEYS: ClassVar[set[str]] = {
        "lang",
        "title",
        "author",
        "description",
        "keywords",
        "published",
        "date",
    }

    DOCUMENT_CSS: ClassVar[str]
    PORTRAIT_CSS: ClassVar[str]
    LANDSCAPE_CSS: ClassVar[str]
    DOCUMENT_SCRIPT: ClassVar[str]
    PAGE_LAYOUTS: ClassVar[tuple[str, ...]] = ("portrait", "landscape")
    DEFAULT_PAGE_LAYOUT: ClassVar[str] = "portrait"

    @classmethod
    def _normalize_orientation(cls, orientation: str) -> str:
        """Normalize and validate a page orientation name."""
        value = orientation.strip().lower()
        if value not in cls.PAGE_LAYOUTS:
            valid = ", ".join(cls.PAGE_LAYOUTS)
            raise ValueError(
                f"Unknown page orientation: {orientation!r} (choose from {valid})"
            )
        return value

    @classmethod
    def _css_for_orientation(cls, orientation: str) -> str:
        """Return the base CSS together with the print CSS for an orientation."""
        value = cls._normalize_orientation(orientation)
        layout_css = cls.PORTRAIT_CSS if value == "portrait" else cls.LANDSCAPE_CSS
        return cls.DOCUMENT_CSS + "\n" + layout_css

    def _heading_slug(self, title: str) -> str:
        """Turn visible heading text into a lowercase, URL-safe anchor id."""
        plain = title
        for char, placeholder in self.ESCAPE_CHARS.items():
            plain = plain.replace(placeholder, char)
        plain = self.HEADING_ID_STRIP_RE.sub("", plain).strip().lower()
        slug = self.HEADING_SLUG_RE.sub("", plain)
        slug = re.sub(r"\s+", "-", slug)
        slug = re.sub(r"-+", "-", slug).strip("-")
        return slug or "section"

    @staticmethod
    def _unique_heading_id(base: str, used: set[str]) -> str:
        """Return ``base`` or a numbered variant not already assigned to a heading."""
        candidate = base
        suffix = 1
        while candidate in used:
            candidate = f"{base}-{suffix}"
            suffix += 1
        used.add(candidate)
        return candidate

    def _parse_front_matter(self, text: str) -> tuple[str, dict[str, str]]:
        """Parse optional YAML-style front matter configurations, returning body text and fields."""
        if not text.startswith("---\n"):
            return text, {}
        lines = text.split("\n")
        end = None
        for i in range(1, len(lines)):
            if lines[i].strip() == "---":
                end = i
                break
        if end is None:
            return text, {}
        front_matter_text = "\n".join(lines[1:end])
        body = "\n".join(lines[end + 1 :])
        front_matter: dict[str, str] = {}
        for line in front_matter_text.splitlines():
            line = line.strip()
            if not line or line.startswith("#") or ":" not in line:
                continue
            key, _, value = line.partition(":")
            key, value = key.strip(), value.strip()
            if len(value) >= 2 and value[0] in "\"'" and value[-1] == value[0]:
                value = value[1:-1]
            if key in self.FRONT_MATTER_KEYS:
                front_matter[key] = value
        if "date" in front_matter and "published" not in front_matter:
            front_matter["published"] = front_matter.pop("date")
        return body, front_matter

    def _build_document(
        self, body: str, front_matter: dict[str, str], orientation: str
    ) -> str:
        """Construct a complete HTML5 document with metadata, CSS and header script."""
        lang = front_matter.get("lang", "")
        lang_attr = f' lang="{lang}"' if lang else ""
        meta_keys = ("author", "description", "keywords")
        head_elements = ['    <meta charset="utf-8" />']
        for key in meta_keys:
            if key in front_matter:
                head_elements.append(
                    f'    <meta name="{key}" content="{front_matter[key]}" />'
                )
        if "title" in front_matter:
            head_elements.append(f"    <title>{front_matter['title']}</title>")
        if "published" in front_matter:
            head_elements.append(
                f'    <meta name="published" content="{front_matter["published"]}" />'
            )
        head_elements.append(
            f"    <style>\n{self._css_for_orientation(orientation)}    </style>"
        )
        html_layout = [
            "<!doctype html>",
            f"<html{lang_attr}>",
            "  <head>",
            *head_elements,
            "  </head>",
            "  <body>",
        ]
        if body:
            html_layout.append(body)
        html_layout.extend([self.DOCUMENT_SCRIPT.rstrip("\n"), "  </body>", "</html>"])
        return "\n".join(html_layout)

    @staticmethod
    def _lang_attr(lang: str) -> str:
        """Generate an HTML language attribute string if a language code is specified."""
        return f' lang="{lang}"' if lang else ""

    @staticmethod
    def _escape_html(text: str) -> str:
        """Convert unsafe special characters to secure HTML entity representations."""
        return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

    @staticmethod
    def _list_item_tag(stripped: str) -> str | None:
        """Return "ul" or "ol" if the line starts a list item, otherwise None."""
        if stripped.startswith(("* ", "- ")):
            return "ul"
        if re.match(r"^\d+\.\s+", stripped):
            return "ol"
        return None

    @staticmethod
    def _line_indent(line: str) -> int:
        """Return the leading whitespace width of a line."""
        return len(line) - len(line.lstrip())

    def _list_item_content(self, tag: str, stripped: str) -> str:
        """Return the processed inline content, including checkbox inputs, for a list item."""
        if tag == "ul":
            content = stripped[2:]
        else:
            content = re.sub(r"^\d+\.\s+", "", stripped)
        if content.startswith(("[x] ", "[X] ")):
            return (
                '<input type="checkbox" checked disabled> '
                + self._apply_inline_rules(content[4:])
            )
        if content.startswith("[ ] "):
            return '<input type="checkbox" disabled> ' + self._apply_inline_rules(
                content[4:]
            )
        return self._apply_inline_rules(content)

    def _render_code_block(self, content: str, lang: str = "") -> str:
        """Render escaped code content inside pre-code containers with a language label."""
        escaped = self._escape_html(content)
        label = (
            f'<div class="code-lang">{self._escape_html(lang)}</div>' if lang else ""
        )
        return f"{label}<pre><code>{escaped}</code></pre>"

    def _render_paragraph(self, buffer_lines: list[str], lang: str = "") -> str:
        """Process buffered lines into a standard HTML paragraph element or figure block."""
        content = self._process_paragraph_breaks(buffer_lines)
        if self._is_figure_block(content):
            return content
        return f"<p{self._lang_attr(lang)}>{content}</p>"

    @staticmethod
    def _is_figure_block(content: str) -> bool:
        """Verify whether the analyzed string forms a standalone figure component boundary."""
        stripped = content.strip()
        return stripped.startswith("<figure>") and stripped.endswith("</figure>")

    def _apply_footnote_refs(self, text: str) -> str:
        """Replace footnote markers with their HTML anchor links."""
        return self.FOOTNOTE_REF_RE.sub(self.FOOTNOTE_REF_HTML, text)

    @staticmethod
    def _find_label_end(text: str, start: int) -> int | None:
        """Locate the ``]`` closing the link label that opens at ``start``.

        Nested ``[...]`` groups are balanced, so a label such as
        ``text [with] brackets`` is matched as a whole.  ``None`` is returned
        when the label is unterminated, spans a line break, or is not followed
        by the opening parenthesis of a destination.
        """
        depth = 0
        for index in range(start, len(text)):
            char = text[index]
            if char == "\n":
                return None
            if char == "[":
                depth += 1
            elif char == "]":
                depth -= 1
                if not depth:
                    return index if text[index + 1 : index + 2] == "(" else None
        return None

    @staticmethod
    def _parse_link_dest(text: str, start: int) -> tuple[str, str, int] | None:
        """Parse the ``url "title")`` part that follows a link label.

        Returns the destination, the optional title and the index just after
        the closing parenthesis, or ``None`` when the destination is
        malformed.  Balanced parentheses are kept inside the destination and
        destinations may be wrapped in angle brackets.
        """
        size = len(text)
        index = start
        if text[index : index + 1] == "<":
            closing = text.find(">", index + 1)
            if closing == -1:
                return None
            url = text[index + 1 : closing]
            index = closing + 1
        else:
            begin = index
            depth = 0
            while index < size:
                char = text[index]
                if char.isspace():
                    break
                if char == "(":
                    depth += 1
                elif char == ")":
                    if not depth:
                        break
                    depth -= 1
                index += 1
            url = text[begin:index]
        title = ""
        cursor = index
        while cursor < size and text[cursor].isspace():
            cursor += 1
        if text[cursor : cursor + 1] in ('"', "'", "("):
            closer = ")" if text[cursor] == "(" else text[cursor]
            title_end = text.find(closer, cursor + 1)
            if title_end == -1:
                return None
            title = text[cursor + 1 : title_end]
            index = title_end + 1
            while index < size and text[index].isspace():
                index += 1
        if text[index : index + 1] != ")":
            return None
        return url, title, index + 1

    def _protect_links(
        self, text: str, links: dict[str, str], allow_links: bool = True
    ) -> str:
        """Replace ``[label](url "title")`` links with placeholder tokens.

        Destinations are recorded verbatim and restored after every other
        inline rule has run, so underscores, asterisks and quotes inside a URL
        can no longer be mistaken for emphasis or typography.  Labels are
        processed recursively, and links inside a label are left as literal
        text because nested anchors are not valid HTML.
        """
        if not allow_links:
            return text
        chunks: list[str] = []
        index = 0
        while index < len(text):
            start = text.find("[", index)
            if start == -1:
                chunks.append(text[index:])
                break
            chunks.append(text[index:start])
            index = start + 1
            label_end = self._find_label_end(text, start)
            if label_end is None:
                chunks.append("[")
                continue
            parsed = self._parse_link_dest(text, label_end + 2)
            if parsed is None:
                chunks.append(text[start : label_end + 1])
                index = label_end + 1
                continue
            url, title, index = parsed
            key = f"\x00LINK{len(links)}\x00"
            label = self._apply_inline_rules(
                text[start + 1 : label_end], allow_links=False
            )
            title_attr = f' title="{title}"' if title else ""
            safe_url = url.replace('"', "&quot;")
            links[key] = f'<a href="{safe_url}"{title_attr}>{label}</a>'
            chunks.append(key)
        return "".join(chunks)

    def _replace_escapes(self, text: str) -> str:
        """Swap escaped characters for internal placeholder tokens."""
        for char, placeholder in self.ESCAPE_CHARS.items():
            text = text.replace(f"\\{char}", placeholder)
        return text

    def _restore_escapes(self, text: str) -> str:
        """Restore placeholder tokens to their target characters."""
        for char, placeholder in self.ESCAPE_CHARS.items():
            clean_char = self.RESTORED_ESCAPES.get(char, char)
            text = text.replace(placeholder, clean_char)
        return text

    def _render_footnotes(self, footnotes: dict[str, str]) -> list[str]:
        """Render collected footnotes inside an HTML ordered list with back-references."""
        if not footnotes:
            return []
        lines = ['<div class="footnotes">\n  <hr>\n  <ol>']
        for fn_id, fn_text in footnotes.items():
            lines.append(
                f'    <li id="fn:{fn_id}">{fn_text} <a href="#fnref:{fn_id}" class="footnote-backref">&uarr;</a></li>'
            )
        lines.append("  </ol>\n</div>")
        return lines

    def _extract_footnotes(self, text: str) -> tuple[str, dict[str, str]]:
        """Extract explicit footnote structural definitions into a dictionary mapping."""
        footnotes: dict[str, str] = {}
        clean_lines: list[str] = []
        for line in text.split("\n"):
            match = self.FOOTNOTE_DEF_RE.match(line.strip())
            if match:
                fn_id, fn_text = match.groups()
                footnotes[fn_id] = self._apply_inline_rules(fn_text)
            else:
                clean_lines.append(line)
        return "\n".join(clean_lines), footnotes

    def _close_quote(
        self, html_lines: list[str], quote_buffer: list[str], lang: str = ""
    ) -> None:
        """Close an open blockquote, wrapping its buffered lines in paragraphs."""
        lang_attr = self._lang_attr(lang)
        html_lines.append(f"<blockquote{lang_attr}>")
        subs, curr = [], []
        for item in quote_buffer:
            if item.strip() == "":
                if curr:
                    subs.append(f"  {self._render_paragraph(curr)}")
                    curr.clear()
            else:
                curr.append(item)
        if curr:
            subs.append(f"  {self._render_paragraph(curr)}")
        html_lines.extend(subs)
        html_lines.append("</blockquote>")

    def _flush_all_buffers(
        self,
        html: list[str],
        p_buf: list[str],
        q_buf: list[str],
        t_rows: list[str],
        p_lang: str = "",
        q_lang: str = "",
        t_lang: str = "",
    ) -> None:
        """Flush pending paragraph, quote, and table buffers to the HTML output."""
        if p_buf:
            html.append(self._render_paragraph(p_buf, p_lang))
            p_buf.clear()
        if q_buf:
            self._close_quote(html, q_buf, q_lang)
            q_buf.clear()
        if t_rows:
            html.append(self._compile_table(t_rows, t_lang))
            t_rows.clear()

    def _table_row(
        self, cells: list[str], alignments: list[str], tag: str = "td"
    ) -> str:
        """Render a list of cell strings into a single formatted HTML table row string."""
        cell_lines: list[str] = []
        for i, cell in enumerate(cells):
            align = alignments[i] if i < len(alignments) else ""
            content = self._apply_inline_rules(cell)
            cell_lines.append(f"      <{tag}{align}>{content}</{tag}>")
        return "\n".join(["    <tr>", *cell_lines, "    </tr>"])

    def _compile_table(self, rows: list[str], lang: str = "") -> str:
        """Compile raw markdown table row strings into a structured HTML table block."""
        if len(rows) < 2:
            return "\n".join(rows)
        footer_idx: int | None = None
        for i, row in enumerate(rows[2:], start=2):
            cells = [c.strip() for c in row.split("|")[1:-1]]
            if all(re.match(r"^:?=+:?$", c) for c in cells):
                footer_idx = i
                break
        align_row = [c.strip() for c in rows[1].split("|")[1:-1]]
        alignments: list[str] = []
        for col in align_row:
            if col.startswith(":") and col.endswith(":"):
                alignments.append(' style="text-align:center;"')
            elif col.endswith(":"):
                alignments.append(' style="text-align:right;"')
            elif col.startswith(":"):
                alignments.append(' style="text-align:left;"')
            else:
                alignments.append("")
        lang_attr = self._lang_attr(lang)
        headers = [c.strip() for c in rows[0].split("|")[1:-1]]
        html = [
            f"<table{lang_attr}>",
            "  <thead>",
            self._table_row(headers, alignments, tag="th"),
            "  </thead>",
        ]
        body_rows = rows[2:footer_idx] if footer_idx else rows[2:]
        if body_rows:
            html.append("  <tbody>")
            for r in body_rows:
                cols = [c.strip() for c in r.split("|")[1:-1]]
                html.append(self._table_row(cols, alignments))
            html.append("  </tbody>")
        footer_rows = rows[footer_idx + 1 :] if footer_idx else []
        if footer_rows:
            html.append("  <tfoot>")
            for r in footer_rows:
                cols = [c.strip() for c in r.split("|")[1:-1]]
                html.append(self._table_row(cols, alignments))
            html.append("  </tfoot>")
        html.append("</table>")
        return "\n".join(html)

    def _process_paragraph_breaks(self, buffer_lines: list[str]) -> str:
        """Convert trailing breaks into <br /> and apply inline rules per line."""
        processed: list[str] = []
        for line in buffer_lines:
            has_break = line.endswith(("  ", "\\"))
            if line.endswith("  "):
                clean = line[:-2]
            elif line.endswith("\\"):
                clean = line[:-1]
            else:
                clean = line
            inline = self._apply_inline_rules(clean.strip())
            if has_break:
                inline += "<br />"
            processed.append(inline)
        return "\n".join(processed)

    def _apply_inline_rules(self, text: str, allow_links: bool = True) -> str:
        """Resolve typographic translations, emojis, inline tags, spans, and tokens.

        Code spans, images, links and footnote markers are shielded with
        placeholder tokens first, so their contents are never touched by the
        emphasis, typography or emoji rules, and are restored at the end.
        ``allow_links`` is disabled while recursing into a link label, since
        links cannot be nested.
        """
        code_spans: dict[str, str] = {}

        def protect_code(match: re.Match[str]) -> str:
            """Replace an inline code span with a placeholder token."""
            key = f"\x00CODE{len(code_spans)}\x00"
            code_spans[key] = match.group(1)
            return key

        text = self.PROTECT_CODE_RE.sub(protect_code, text)
        img_tags: dict[str, str] = {}

        def protect_image(match: re.Match[str]) -> str:
            """Replace an image reference with a placeholder and record its figure HTML."""
            key = f"\x00IMG{len(img_tags)}\x00"
            alt = match.group(1)
            src = match.group(2)
            title = match.group(3)
            title_attr = f' title="{title}"' if title else ""
            img = f'<img src="{src}" alt="{alt}"{title_attr}>'
            if title:
                img_tags[key] = (
                    f"<figure>\n  {img}\n  <figcaption>{title}</figcaption>\n</figure>"
                )
            else:
                img_tags[key] = f"<figure>\n  {img}\n</figure>"
            return key

        text = self.IMAGE_RE.sub(protect_image, text)
        links: dict[str, str] = {}
        text = self._protect_links(text, links, allow_links)
        footnote_refs: dict[str, str] = {}

        def protect_footnote_ref(match: re.Match[str]) -> str:
            """Replace a footnote marker with a placeholder token."""
            key = f"\x00FNREF{len(footnote_refs)}\x00"
            footnote_refs[key] = self._apply_footnote_refs(match.group(0))
            return key

        text = self.FOOTNOTE_REF_RE.sub(protect_footnote_ref, text)

        def match_emoji(match: re.Match[str]) -> str:
            """Return the emoji for a shortcode, or the original token if unknown."""
            return self.EMOJIS.get(match.group(1), match.group(0))

        text = self.EMOJI_RE.sub(match_emoji, text)

        for pattern, replacement in self.TYPOGRAPHY_RULES:
            text = pattern.sub(replacement, text)

        text = self.RUBY_RE.sub(r"<ruby>\1<rp>(</rp><rt>\2</rt><rp>)</rp></ruby>", text)

        for pattern, replacement in self.INLINE_RULES:
            text = pattern.sub(replacement, text)

        text = self.INLINE_LANG_RE.sub(r'<span lang="\1">\2</span>', text)

        # Restore in reverse order of protection: a link label may contain a
        # code span or image token, so those placeholders must already exist in
        # the final text by the time the link HTML itself is put back.
        for key, tag in footnote_refs.items():
            text = text.replace(key, tag)

        for key, tag in links.items():
            text = text.replace(key, tag)

        for key, tag in img_tags.items():
            text = text.replace(key, tag)

        for key, content in code_spans.items():
            escaped = self._escape_html(content)
            text = text.replace(key, f"<code>{escaped}</code>")

        return text

    def convert(
        self,
        text: str,
        orientation: str = DEFAULT_PAGE_LAYOUT,
        *,
        page_layout: str | None = None,
    ) -> str:
        """Convert Markdown into a complete, styled HTML5 document.

        ``orientation`` (or its alias ``page_layout``) selects the print CSS:
        ``"portrait"`` (default) or ``"landscape"``.
        """
        if not text.strip():
            return ""

        selected_orientation = self._normalize_orientation(
            page_layout if page_layout is not None else orientation
        )
        text, front_matter = self._parse_front_matter(text)
        text = self._replace_escapes(text)
        text, footnotes = self._extract_footnotes(text)

        lines = text.split("\n")
        html_lines: list[str] = []
        used_heading_ids: set[str] = set()

        in_blockquote = False
        in_code_block = in_table = in_def_list = False

        paragraph_buffer: list[str] = []
        code_buffer: list[str] = []
        quote_buffer: list[str] = []
        table_rows: list[str] = []

        paragraph_lang = quote_lang = table_lang = code_lang = ""
        list_just_closed = False

        list_stack: list[_ListFrame] = []

        def flush_pending() -> None:
            """Flush all open structural buffers into the HTML output and reset languages."""
            nonlocal paragraph_lang, quote_lang, table_lang
            self._flush_all_buffers(
                html_lines,
                paragraph_buffer,
                quote_buffer,
                table_rows,
                p_lang=paragraph_lang,
                q_lang=quote_lang,
                t_lang=table_lang,
            )
            paragraph_lang = quote_lang = table_lang = ""

        def item_pad(depth: int) -> str:
            """Return the indentation for an <li> element at the given depth."""
            return "  " * (2 * depth - 1)

        def list_pad(depth: int) -> str:
            """Return the indentation for a <ul>/<ol> element at the given depth."""
            return "  " * (2 * (depth - 1))

        def close_pending_li_at(depth: int) -> None:
            """Close the deferred <li> of the list at the given 1-based depth."""
            frame = list_stack[depth - 1]
            if frame.li_pending:
                html_lines.append(f"{item_pad(depth)}</li>")
                frame.li_pending = False

        def pop_level() -> None:
            """Close the deepest open list, including any deferred <li>."""
            depth = len(list_stack)
            frame = list_stack[-1]
            if frame.li_pending:
                html_lines.append(f"{item_pad(depth)}</li>")
            html_lines.append(f"{list_pad(depth)}</{frame.tag}>")
            list_stack.pop()

        def close_all_lists() -> None:
            """Close every open list level."""
            while list_stack:
                pop_level()

        def open_level(tag: str, indent: int) -> None:
            """Open a new <ul>/<ol> at a fresh depth."""
            depth = len(list_stack) + 1
            html_lines.append(f"{list_pad(depth)}<{tag}{self._lang_attr(block_lang)}>")
            list_stack.append(_ListFrame(tag, indent, False))

        def switch_level_tag(tag: str) -> None:
            """Replace the tag of the current list (type switch is not indented)."""
            depth = len(list_stack)
            frame = list_stack[-1]
            close_pending_li_at(depth)
            html_lines.append(f"{list_pad(depth)}</{frame.tag}>")
            lang_attr = self._lang_attr(block_lang) if depth == 1 else ""
            html_lines.append(f"{list_pad(depth)}<{tag}{lang_attr}>")
            list_stack[-1] = _ListFrame(tag, frame.indent, False)

        def ensure_open_list(tag: str, item_indent: int) -> None:
            """Adjust open lists so the top of the stack matches the item."""
            while list_stack and list_stack[-1].indent > item_indent:
                pop_level()
            if not list_stack or list_stack[-1].indent < item_indent:
                open_level(tag, item_indent)
            elif list_stack[-1].tag != tag:
                switch_level_tag(tag)

        def has_nested_children(line_index: int, own_indent: int) -> bool:
            """Return True if the next non-blank list line is more deeply indented."""
            for j in range(line_index + 1, len(lines)):
                nxt_stripped = lines[j].strip()
                if not nxt_stripped:
                    continue
                if self._list_item_tag(nxt_stripped) is None:
                    return False
                return self._line_indent(lines[j]) > own_indent
            return False

        for line_index, line in enumerate(lines):
            stripped = line.strip()

            if stripped.startswith("```"):
                if in_code_block:
                    code_content = "\n".join(code_buffer)
                    html_lines.append(self._render_code_block(code_content, code_lang))
                    code_buffer.clear()
                    in_code_block = False
                    code_lang = ""
                else:
                    flush_pending()
                    code_lang = stripped[3:].strip()
                    in_code_block = True
                continue

            if in_code_block:
                code_buffer.append(line)
                continue

            block_lang = ""
            lang_match = self.BLOCK_LANG_RE.match(line)
            if lang_match:
                block_lang = lang_match.group(1)
                line = lang_match.group(2)
                stripped = line.strip()

            comment_match = self.COMMENT_RE.match(stripped)
            if comment_match:
                flush_pending()
                html_lines.append(f"<!--{comment_match.group(1)}-->")
                continue

            list_item_tag = self._list_item_tag(stripped)
            is_quote_item = stripped.startswith(">")
            is_table_row = stripped.startswith("|") and stripped.endswith("|")
            is_def_desc = stripped.startswith(": ")

            heading_match = self.HEADING_RE.match(stripped)
            is_hr = bool(self.HR_RE.match(stripped))
            is_static_block = bool(heading_match or is_hr)

            if (
                list_item_tag is not None
                or is_quote_item
                or is_static_block
                or is_table_row
                or is_def_desc
                or not stripped
            ) and paragraph_buffer:
                html_lines.append(
                    self._render_paragraph(paragraph_buffer, paragraph_lang)
                )
                paragraph_buffer.clear()
                paragraph_lang = ""

            if not is_quote_item and in_blockquote:
                self._close_quote(html_lines, quote_buffer, quote_lang)
                quote_buffer.clear()
                in_blockquote = False
                quote_lang = ""

            if not is_table_row and in_table:
                html_lines.append(self._compile_table(table_rows, table_lang))
                table_rows.clear()
                in_table = False
                table_lang = ""

            if is_table_row:
                if not in_table:
                    table_lang = block_lang
                in_table = True
                table_rows.append(stripped)
                continue

            if is_def_desc:
                if not in_def_list:
                    in_def_list = True
                    term, lang_attr = "", ""
                    if html_lines:
                        term_line = html_lines[-1]
                        term_match = re.match(
                            r'^<p( lang="[^"]*")?>([\s\S]*)</p>$', term_line
                        )
                        if term_match:
                            html_lines.pop()
                            if term_match.group(1):
                                lang_attr = term_match.group(1)
                            term = term_match.group(2)
                        elif not term_line.startswith("<"):
                            term = html_lines.pop()
                    if block_lang:
                        lang_attr = self._lang_attr(block_lang)
                    html_lines.append(f"<dl{lang_attr}>")
                    if term:
                        html_lines.append(
                            f"  <dt>{self._apply_inline_rules(term)}</dt>"
                        )

                desc_content = stripped[2:]
                html_lines.append(
                    f"  <dd>{self._apply_inline_rules(desc_content)}</dd>"
                )
                continue

            if in_def_list and not is_def_desc and stripped:
                html_lines.append("</dl>")
                in_def_list = False

            if list_item_tag is not None:
                content = self._list_item_content(list_item_tag, stripped)
                item_indent = self._line_indent(line)

                ensure_open_list(list_item_tag, item_indent)
                depth = len(list_stack)
                close_pending_li_at(depth)

                if has_nested_children(line_index, item_indent):
                    html_lines.append(f"{item_pad(depth)}<li>{content}")
                    list_stack[-1].li_pending = True
                else:
                    html_lines.append(f"{item_pad(depth)}<li>{content}</li>")
                list_just_closed = False
                continue

            if list_stack:
                close_all_lists()
                list_just_closed = True

            if is_quote_item:
                if not in_blockquote:
                    quote_lang = block_lang
                in_blockquote = True
                content = (
                    line.lstrip()[2:] if stripped.startswith("> ") else stripped[1:]
                )
                quote_buffer.append(self._apply_inline_rules(content))
                continue

            if not stripped:
                if list_just_closed:
                    html_lines.append("<!-- -->")
                    list_just_closed = False
                continue

            list_just_closed = False

            if heading_match:
                hashes, title = heading_match.groups()
                level = len(hashes)

                id_match = re.search(r"\s+\{#([a-zA-Z0-9_-]+)\}$", title)
                if id_match:
                    heading_id = id_match.group(1)
                    title = title[: id_match.start()]
                    used_heading_ids.add(heading_id)
                else:
                    heading_id = self._unique_heading_id(
                        self._heading_slug(title), used_heading_ids
                    )
                id_attr = f' id="{heading_id}"'

                lang_attr = self._lang_attr(block_lang)
                title = self._apply_inline_rules(title)
                html_lines.append(f"<h{level}{id_attr}{lang_attr}>{title}</h{level}>")
                continue

            if is_hr:
                html_lines.append("<hr>")
                continue

            if not paragraph_buffer and block_lang:
                paragraph_lang = block_lang
            paragraph_buffer.append(line)

        flush_pending()
        close_all_lists()
        if in_def_list:
            html_lines.append("</dl>")

        html_lines.extend(self._render_footnotes(footnotes))

        final_html = "\n".join(html_lines)
        final_html = self._restore_escapes(final_html)
        return self._build_document(final_html, front_matter, selected_orientation)


MarkdownToHTML.DOCUMENT_CSS = r"""/* Base Rules */
:root {
  --bg-page: #ffffff;
  --bg-subtle: #f5f5f5;
  --bg-row-even: #fafafa;
  --text-main: #000000;
  --text-muted: #525252;
  --border-color: #000000;
  --border-subtle: #e0e0e0;
  --accent-mark: #ffff00;
  --font-serif: "Noto Serif", "Liberation Serif", "Times New Roman", serif;
  --font-sans: "Noto Sans", "Liberation Sans", Arial, sans-serif;
  --font-mono: "Noto Sans Mono", "Liberation Mono", monospace;
  --radius-sm: 4px;
  --space-base: 24px;
  --code-padding-x: 16px;
  --print-header: none;
}
*, *::before, *::after {
  box-sizing: border-box;
}
body {
  margin: 0;
  padding: var(--space-base) var(--space-base) var(--space-base) calc(var(--space-base) * 2);
  font-family: var(--font-serif);
  font-size: 16px;
  line-height: 1.5;
  color: var(--text-main);
  background-color: var(--bg-page);
}
h1, h2, h3, h4, h5, h6 {
  margin: 1.3em 0 0.5em;
  font-family: var(--font-sans);
  font-weight: bold;
  line-height: 1.25;
  overflow-wrap: break-word;
}
h1 { font-size: 28px; margin-top: 0; }
h2 { font-size: 24px; }
h2#toc { font-style: italic; }
h3 { font-size: 20px; }
h4 { font-size: 18px; }
h5 { font-size: 16px; }
h6 { font-size: 16px; font-style: italic; }
p {
  margin: 0.9em 0;
  overflow-wrap: break-word;
}
hr {
  height: 2px;
  margin: 24px 0;
  border: none;
  background-color: var(--border-color);
}
blockquote {
  margin: 1.2em 0;
  padding: 12px 20px;
  border-left: 4px solid var(--border-color);
  background-color: var(--bg-subtle);
  font-style: italic;
  overflow-wrap: break-word;
}
blockquote > :first-child { margin-top: 0; }
blockquote > :last-child { margin-bottom: 0; }
mark {
  padding: 2px 5px;
  border-radius: var(--radius-sm);
  background-color: var(--accent-mark);
  color: var(--text-main);
}
a:link { color: #0000cd; text-underline-offset: 2px; }
a:visited { color: #9400d3; }
a:hover, a:focus { outline: none; color: #000080; }
a:active { color: #dc143c; }
ol, ul {
  margin: 1em 0;
  padding-left: 0;
  list-style: none;
  overflow-wrap: break-word;
}
li > ol, li > ul {
  margin: 0.4em 0 0.5em;
  padding-left: 22px;
}
li > ol:last-child, li > ul:last-child {
  margin-bottom: 0;
}
ol {
  counter-reset: custom-counter;
}
li {
  position: relative;
  padding-left: 26px;
  margin-bottom: 0.4em;
  overflow-wrap: break-word;
}
li:last-child {
  margin-bottom: 0;
}
ul > li::before {
  content: "•";
  position: absolute;
  left: 8px;
  top: 0;
}
ul ul > li::before { content: "◦"; }
ul ul ul > li::before { content: "▪"; }
ul.task-list > li,
ul > li:has(input[type="checkbox"]) {
  padding-left: 4px;
}
ul.task-list > li::before,
ul > li:has(input[type="checkbox"])::before {
  display: none;
}
ol > li {
  counter-increment: custom-counter;
}
ol > li::before {
  content: counter(custom-counter) ".";
  position: absolute;
  left: 0;
  top: 0;
  font-variant-numeric: tabular-nums;
}
ol ol > li::before { content: counter(custom-counter, lower-alpha) "."; }
ol ol ol > li::before { content: counter(custom-counter, lower-roman) "."; }
ol li input[type="checkbox"],
ul li input[type="checkbox"] {
  position: static;
  display: inline-block;
  width: 15px;
  height: 15px;
  margin: 0 8px 0 0;
  vertical-align: -2px;
  accent-color: var(--text-main);
}
dl { margin: 1.2em 0; }
dt {
  margin-top: 0.9em;
  font-weight: bold;
  overflow-wrap: anywhere;
}
dd {
  margin: 0.25em 0 0;
  padding-left: 14px;
  border-left: 2px solid var(--border-subtle);
  font-style: italic;
  overflow-wrap: break-word;
}
code {
  padding: 2px 5px;
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-sm);
  background-color: var(--bg-subtle);
  font-family: var(--font-mono);
  font-size: 0.88em;
  line-height: 1;
  overflow-wrap: anywhere;
}
div.code-lang {
  display: block;
  width: fit-content;
  position: relative;
  z-index: 2;
  margin: 1.2em calc(var(--code-padding-x) + 1px) -10px auto;
  padding: 3px 10px;
  border: 1px solid var(--border-color);
  border-radius: var(--radius-sm);
  font-family: var(--font-mono);
  font-size: 0.8em;
  font-weight: bold;
  line-height: 1;
  background-color: var(--text-main);
  color: var(--bg-page);
}
pre {
  position: relative;
  z-index: 1;
  max-width: 100%;
  margin: 1.2em 0;
  padding: 16px var(--code-padding-x);
  border: 1px solid var(--border-color);
  background-color: var(--bg-subtle);
  overflow-x: auto;
}
div.code-lang + pre {
  margin-top: 0;
  padding-top: 22px;
}
pre > code {
  display: block;
  margin: 0;
  padding: 0;
  border: none;
  border-radius: 0;
  line-height: 1.45;
  background-color: transparent;
  white-space: pre;
  overflow-wrap: normal;
}
table {
  width: 100%;
  margin: 1.5em 0;
  border-collapse: collapse;
  border: 1px solid var(--border-color);
}
th, td {
  padding: 10px 14px;
  text-align: left;
  border: 1px solid var(--border-color);
  overflow-wrap: anywhere;
}
thead tr {
  background-color: var(--text-main);
  color: var(--bg-page);
}
thead th {
  font-family: var(--font-sans);
  font-weight: bold;
}

tbody tr:nth-child(even) {
  background-color: var(--bg-row-even);
}
tfoot tr {
  background-color: var(--bg-subtle);
  font-style: italic;
}
figure {
  display: block;
  margin: 1.2em 0;
}
figure img {
  display: block;
  max-width: 100%;
  height: auto;
}
figcaption {
  margin-top: 6px;
  font-size: 0.9em;
  font-style: italic;
  color: var(--text-muted);
  overflow-wrap: break-word;
}
ruby { ruby-position: over; ruby-align: space-around; }
rt { letter-spacing: 0.05em; font-size: 0.55em; white-space: nowrap; }
rp { display: none; }
span[lang="ja"] { font-family: "Noto Serif CJK JP", "Source Han Serif JP", serif; }
span[lang="zh-CN"], span[lang="zh-Hans"] { font-family: "Noto Serif CJK SC", "Source Han Serif SC", serif; }
span[lang="zh-TW"], span[lang="zh-Hant"] { font-family: "Noto Serif CJK TC", "Source Han Serif TC", serif; }
span[lang="zh-HK"] { font-family: "Noto Serif CJK HK", "Source Han Serif HK", serif; }
span[lang="ko"] { font-family: "Noto Serif CJK KR", "Source Han Serif KR", serif; }
"""

MarkdownToHTML.PORTRAIT_CSS = r"""/* Portrait PDF/Print */
@page {
  size: A4 portrait;
  margin: 22mm 15mm 20mm 25mm;
  @top-center {
    content: var(--print-header);
    font-family: var(--font-sans);
    font-size: 8.5pt;
    color: var(--text-muted);
    vertical-align: bottom;
    padding-bottom: 6pt;
    border-bottom: 0.5pt solid var(--border-subtle);
  }
  @bottom-center {
    content: counter(page);
    font-family: var(--font-sans);
    font-size: 8.5pt;
    color: var(--text-muted);
    vertical-align: top;
    padding-top: 6pt;
  }
}
@media print {
  * {
    -webkit-print-color-adjust: exact;
    print-color-adjust: exact;
  }
  body {
    padding: 0;
    font-size: 11pt;
    line-height: 1.45;
    color: #000000;
    background-color: #ffffff;
  }
  h1 { font-size: 20pt; }
  h2 { font-size: 17pt; }
  h3 { font-size: 14.5pt; }
  h4 { font-size: 12.5pt; }
  h5, h6 { font-size: 11pt; }
  h1, h2, h3, h4, h5, h6, dt, div.code-lang {
    break-after: avoid;
    page-break-after: avoid;
  }
  blockquote, figure, pre, tr {
    break-inside: avoid;
    page-break-inside: avoid;
  }
  p, li {
    orphans: 3;
    widows: 3;
  }
  pre {
    overflow: visible;
  }
  pre > code {
    white-space: pre-wrap;
    overflow-wrap: break-word;
  }
  thead {
    display: table-header-group;
  }
  tfoot {
    display: table-footer-group;
  }
  a:link, a:visited {
    color: #000000;
    text-decoration: underline;
    text-decoration-thickness: 1px;
  }
  a[href^="http"]::after {
    content: " (" attr(href) ")";
    font-family: var(--font-mono);
    font-size: 0.85em;
    color: var(--text-muted);
    word-break: break-all;
  }
}
"""

MarkdownToHTML.LANDSCAPE_CSS = r"""/* Landscape PDF/Print */
@page {
  size: A4 landscape;
  margin: 16mm 16mm 16mm 32mm;
  @top-center {
    content: var(--print-header);
    font-family: var(--font-sans);
    font-size: 8.5pt;
    color: var(--text-muted);
    vertical-align: bottom;
    padding-bottom: 5pt;
    border-bottom: 0.5pt solid var(--border-subtle);
  }
  @bottom-center {
    content: counter(page);
    font-family: var(--font-sans);
    font-size: 8.5pt;
    color: var(--text-muted);
    vertical-align: top;
    padding-top: 5pt;
  }
}
@media print {
  * {
    -webkit-print-color-adjust: exact;
    print-color-adjust: exact;
  }
  body {
    padding: 0;
    font-size: 11pt;
    line-height: 1.45;
    color: #000000;
    background-color: #ffffff;
  }
  h1 { font-size: 20pt; }
  h2 { font-size: 17pt; }
  h3 { font-size: 14.5pt; }
  h4 { font-size: 12.5pt; }
  h5, h6 { font-size: 11pt; }
  h1, h2, h3, h4, h5, h6, dt, div.code-lang {
    break-after: avoid;
    page-break-after: avoid;
  }
  blockquote, figure, pre, tr {
    break-inside: avoid;
    page-break-inside: avoid;
  }
  p, li {
    orphans: 3;
    widows: 3;
  }
  pre {
    overflow: visible;
  }
  pre > code {
    white-space: pre-wrap;
    overflow-wrap: break-word;
  }
  thead {
    display: table-header-group;
  }
  tfoot {
    display: table-footer-group;
  }
  a:link, a:visited {
    color: #000000;
    text-decoration: underline;
    text-decoration-thickness: 1px;
  }
  a[href^="http"]::after {
    content: " (" attr(href) ")";
    font-family: var(--font-mono);
    font-size: 0.85em;
    color: var(--text-muted);
    word-break: break-all;
  }
}
"""

MarkdownToHTML.DOCUMENT_SCRIPT = r"""    <script>
      (() => {
        const author = document.querySelector('meta[name="author"]')?.content.trim() || '';
        const title = document.title.trim() || '';
        const published = document.querySelector('meta[name="published"], meta[name="date"]')?.content.trim() || '';

        const base = [author, title].filter(Boolean).join(', ');
        const headerText = published ? (base ? `${base} (${published})` : published) : base;

        if (headerText) {
          const safeText = headerText.replace(/\\/g, '\\\\').replace(/"/g, '\\"');
          document.documentElement.style.setProperty('--print-header', `"${safeText}"`);
        }
      })();
    </script>
"""
