from __future__ import annotations

import re
from typing import ClassVar, Pattern


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
        "|": "|",
    }

    INLINE_RULES: ClassVar[list[tuple[Pattern[str], str]]] = [
        (re.compile(r"\*\*\*(.*?)\*\*\*"), r"<strong><em>\1</em></strong>"),
        (re.compile(r"___(.*?)___"), r"<strong><em>\1</em></strong>"),
        (re.compile(r"\*\*(.*?)\*\*"), r"<strong>\1</strong>"),
        (re.compile(r"__(.*?)__"), r"<strong>\1</strong>"),
        (re.compile(r"\*(.*?)\*"), r"<em>\1</em>"),
        (re.compile(r"_(.*?)_"), r"<em>\1</em>"),
        (re.compile(r"~~(.*?)~~"), r"<s>\1</s>"),
        (re.compile(r"==(.*?)=="), r"<mark>\1</mark>"),
        (re.compile(r"\~(.*?)\~"), r"<sub>\1</sub>"),
        (re.compile(r"\^\^\^(.*?)\^\^\^"), r"<u><em>\1</em></u>"),
        (re.compile(r"\^\^(.*?)\^\^"), r"<u>\1</u>"),
        (re.compile(r"\^(.*?)\^"), r"<sup>\1</sup>"),
        (re.compile(r"\[(.*?)\]\((.*?)\)"), r'<a href="\2">\1</a>'),
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

    FOOTNOTE_REF_RE: ClassVar[Pattern[str]] = re.compile(r"\[\^([a-zA-Z0-9]+)\]")
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
    HR_RE: ClassVar[Pattern[str]] = re.compile(r"^(?:-{3,}|\*{3,}|_{3,})$")
    RUBY_RE: ClassVar[Pattern[str]] = re.compile(r"\{([^{}:|]+)\|([^}]+)\}")
    PROTECT_CODE_RE: ClassVar[Pattern[str]] = re.compile(r"`([^`\n]+)`")
    FOOTNOTE_DEF_RE: ClassVar[Pattern[str]] = re.compile(
        r"^\[\^([a-zA-Z0-9]+)\]:\s+(.*?)$"
    )

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
            if len(value) >= 2 and value == value[-1] and value in "\"'":
                value = value[1:-1]
            if key in self.FRONT_MATTER_KEYS:
                front_matter[key] = value
        if "date" in front_matter and "published" not in front_matter:
            front_matter["published"] = front_matter.pop("date")
        return body, front_matter

    def _build_document(
        self, body: str, front_matter: dict[str, str], include_css: bool = False
    ) -> str:
        """Construct a complete HTML5 document structure containing meta headers and layouts."""
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
        if include_css:
            head_elements.append(f"    <style>\n{self.DOCUMENT_CSS}    </style>")
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
        html_layout.extend(["  </body>", "</html>"])
        return "\n".join(html_layout)

    @staticmethod
    def _lang_attr(lang: str) -> str:
        """Generate an HTML language attribute string if a language code is specified."""
        return f' lang="{lang}"' if lang else ""

    @staticmethod
    def _escape_html(text: str) -> str:
        """Convert unsafe special characters to secure HTML entity representations."""
        return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

    def _render_code_block(self, content: str, lang: str = "") -> str:
        """Render escaped code content inside pre-code containers with a language label."""
        escaped = self._escape_html(content)
        label = f'<div class="code-lang">&sol;{lang}&sol;</div>' if lang else ""
        return f"{label}<pre><code>{escaped}</code></pre>"

    def _render_paragraph(self, buffer_lines: list[str], lang: str = "") -> str:
        """Process buffered lines into a standard HTML paragraph element or figure block."""
        content = self._process_paragraph_breaks(buffer_lines)
        if self._is_figure_block(content):
            return content
        return f"<p{self._lang_attr(lang)}>{content}</p>"

    def _wrap_paragraph(self, buffer_lines: list[str]) -> str:
        """Wrap active block buffer strings inside an anonymous HTML paragraph tag context."""
        content = self._process_paragraph_breaks(buffer_lines)
        if self._is_figure_block(content):
            return content
        return f"<p>{content}</p>"

    @staticmethod
    def _is_figure_block(content: str) -> bool:
        """Verify whether the analyzed string forms a standalone figure component boundary."""
        stripped = content.strip()
        return stripped.startswith("<figure>") and stripped.endswith("</figure>")

    def _apply_footnote_refs(self, text: str) -> str:
        """Substitute markdown pattern footnote markers with operational anchor components."""
        return self.FOOTNOTE_REF_RE.sub(self.FOOTNOTE_REF_HTML, text)

    def _replace_escapes(self, text: str) -> str:
        """Swap explicit escape sequence syntax declarations with intermediate placeholders."""
        for char, placeholder in self.ESCAPE_CHARS.items():
            text = text.replace(f"\\{char}", placeholder)
        return text

    def _restore_escapes(self, text: str) -> str:
        """Revert internal tokens back to safe text characters or target replacements."""
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

    def _close_containers(
        self, lines: list[str], ul: bool = False, ol: bool = False
    ) -> None:
        """Append container closing elements to the current HTML lines stack context."""
        if ul:
            lines.append("</ul>")
        if ol:
            lines.append("</ol>")

    def _close_quote(
        self, html_lines: list[str], quote_buffer: list[str], lang: str = ""
    ) -> None:
        """Flush and compile the active blockquote list data inside container tags."""
        lang_attr = self._lang_attr(lang)
        html_lines.append(f"<blockquote{lang_attr}>")
        subs, curr = [], []
        for item in quote_buffer:
            if item.strip() == "":
                if curr:
                    subs.append(f"  {self._wrap_paragraph(curr)}")
                    curr.clear()
            else:
                curr.append(item)
        if curr:
            subs.append(f"  {self._wrap_paragraph(curr)}")
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
        """Clear all active structural compilation buffers and write output to stacks."""
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
        """Evaluate trailing line breaks and format paragraph internals into lines."""
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

    def _apply_inline_rules(self, text: str) -> str:
        """Resolve typographic translations, emojis, inline tags, spans, and tokens."""
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
        text = self._apply_footnote_refs(text)

        for key, content in code_spans.items():
            escaped = self._escape_html(content)
            text = text.replace(key, f"<code>{escaped}</code>")

        for key, tag in img_tags.items():
            text = text.replace(key, tag)

        return text

    def convert(self, text: str, include_css: bool = False) -> str:
        """Convert a structural Markdown source text into standard clean HTML strings."""
        if not text.strip():
            return ""

        text, front_matter = self._parse_front_matter(text)
        text = self._replace_escapes(text)
        text, footnotes = self._extract_footnotes(text)

        lines = text.split("\n")
        html_lines: list[str] = []

        in_ul = in_ol = in_blockquote = False
        in_code_block = in_table = in_def_list = False

        paragraph_buffer: list[str] = []
        code_buffer: list[str] = []
        quote_buffer: list[str] = []
        table_rows: list[str] = []

        paragraph_lang = quote_lang = table_lang = code_lang = ""
        list_just_closed = False

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

        for line in lines:
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

            is_ul_item = stripped.startswith(("* ", "- "))
            is_ol_item = bool(re.match(r"^\d+\.\s+", stripped))
            is_quote_item = stripped.startswith(">")
            is_table_row = stripped.startswith("|") and stripped.endswith("|")
            is_def_desc = stripped.startswith(": ")

            heading_match = self.HEADING_RE.match(stripped)
            is_hr = bool(self.HR_RE.match(stripped))
            is_static_block = bool(heading_match or is_hr)

            if (
                is_ul_item
                or is_ol_item
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

            if is_ul_item:
                if not in_ul:
                    self._close_containers(html_lines, ol=in_ol)
                    in_ol = False
                    ul_lang = self._lang_attr(block_lang)
                    html_lines.append(f"<ul{ul_lang}>")
                    in_ul = True

                content = stripped[2:]
                if content.startswith(("[x] ", "[X] ")):
                    content = (
                        '<input type="checkbox" checked disabled> '
                        + self._apply_inline_rules(content[4:])
                    )
                elif content.startswith("[ ] "):
                    content = (
                        '<input type="checkbox" disabled> '
                        + self._apply_inline_rules(content[4:])
                    )
                else:
                    content = self._apply_inline_rules(content)

                html_lines.append(f"  <li>{content}</li>")
                list_just_closed = False
                continue

            if is_ol_item:
                if not in_ol:
                    self._close_containers(html_lines, ul=in_ul)
                    in_ul = False
                    ol_lang = self._lang_attr(block_lang)
                    html_lines.append(f"<ol{ol_lang}>")
                    in_ol = True
                content = re.sub(r"^\d+\.\s+", "", stripped)
                content = self._apply_inline_rules(content)
                html_lines.append(f"  <li>{content}</li>")
                list_just_closed = False
                continue

            if in_ul or in_ol:
                self._close_containers(html_lines, ul=in_ul, ol=in_ol)
                list_just_closed = True
                in_ul = in_ol = False

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
                id_attr = ""
                if id_match:
                    id_attr = f' id="{id_match.group(1)}"'
                    title = title[: id_match.start()]

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
        self._close_containers(html_lines, ul=in_ul, ol=in_ol)
        if in_def_list:
            html_lines.append("</dl>")

        html_lines.extend(self._render_footnotes(footnotes))

        final_html = "\n".join(html_lines)
        final_html = self._restore_escapes(final_html)
        if front_matter or include_css:
            return self._build_document(final_html, front_matter, include_css)
        return final_html


MarkdownToHTML.DOCUMENT_CSS = """body {
  padding: 20px;
  font-family: "Noto Serif", "Liberation Serif", "Times New Roman", Times, serif;
  font-size: 18px;
  line-height: 1.4;
  color: #000000;
}
h1, h2, h3, h4, h5, h6 {
  margin-top: 1.2em;
  margin-bottom: 0.6em;
  font-family: "Noto Sans", "Liberation Sans", Arial, sans-serif;
  font-weight: bold;
}
h1 { font-size: 32px; }
h2 { font-size: 28px; }
h3 { font-size: 24px; }
h4 { font-size: 20px; }
h5 { font-size: 18px; }
h6 { font-size: 18px; font-style: italic; }
hr { height: 4px; margin: 20px 0; border: none; background-color: #000000; }
li { position: relative; padding-left: 20px; }
dt { font-weight: bold; }
dd { position: relative; margin-left: 0; padding-left: 20px; font-style: italic; }
blockquote { margin-left: 0; padding-left: 20px; border-left: 8px solid #f5f5f5; }
mark { padding: 0 2px; border-radius: 4px; background-color: #ffff00; }
a:link { color: #0000cd; }
a:visited { color: #9400d3; }
a:hover, a:focus { outline: none; color: #000080; }
a:active { color: #dc143c; }
code {
  padding: 2px 4px;
  border-radius: 4px;
  font-family: "Noto Sans Mono", "Liberation Mono", "Courier New", Courier, monospace;
  font-size: 0.9em;
  line-height: 1;
}
pre {
  max-width: 100%;
  margin: 0;
  padding: 20px;
  border: 1px solid #000000;
  background-color: #f5f5f5;
  overflow: auto;
  scrollbar-color: #000000 transparent;
}
pre > code {
  display: block;
  margin: 0;
  padding: 0;
  border: none;
  border-radius: 0;
  line-height: 1.2;
  background-color: transparent;
  overflow: visible;
}
div.code-lang {
  display: block;
  padding: 10px 20px;
  font-family: "Noto Sans Mono", "Liberation Mono", "Courier New", Courier, monospace;
  font-size: 0.9em;
  line-height: 1;
  background-color: #000000;
  color: #ffffff;
  font-weight: bold;
}
table { margin: 20px 0; border-collapse: collapse; }
th, td { padding: 10px 12px; border: 1px solid #000000; }
th { font-weight: bold; }
thead tr { background-color: #000000; color: #ffffff; }
tfoot tr { background-color: #f5f5f5; font-style: italic; }
figure { display: block; margin: 0; }
figure img { display: block; max-width: 100%; height: auto; }
figcaption { text-align: left; font-style: italic; }
ruby { ruby-position: over; }
rt { letter-spacing: 0.05em; font-size: 0.55em; line-break: strict; }
rp { display: none; }
span[lang="ja"] { font-family: "Noto Serif CJK JP", "Source Han Serif JP", "源ノ明朝", "Source Han Serif", "Hiragino Mincho ProN", "Hiragino Mincho Pro", "IPAexMincho", "IPAMincho", "MS PMincho", "MS Mincho", serif; }
span[lang="zh-CN"], span[lang="zh-Hans"] { font-family: "Noto Serif CJK SC", "Source Han Serif SC", "思源宋体", "Source Han Serif CN", "Source Han Serif", "Songti SC", "FandolSong", "WenQuanYi Bitmap Song", "SimSun", serif; }
span[lang="zh-TW"], span[lang="zh-Hant"] { font-family: "Noto Serif CJK TC", "Source Han Serif TC", "思源宋體", "Source Han Serif TW", "Source Han Serif", "Apple LiSung", "LiSong Pro", "HanaMinA", "PMingLiU", "MingLiU", serif; }
span[lang="zh-HK"] { font-family: "Noto Serif CJK HK", "Source Han Serif HK", "思源宋體 香港", "思源宋體", "Source Han Serif", "Apple LiSung", "LiSong Pro", "HanaMinA", "MingLiU_HKSCS", "PMingLiU", "MingLiU", serif; }
span[lang="ko"] { font-family: "Noto Serif CJK KR", "Source Han Serif KR", "본명조", "Source Han Serif", "AppleMyungjo", "UnBatang", "은바탕", "Batang", serif; }
"""
