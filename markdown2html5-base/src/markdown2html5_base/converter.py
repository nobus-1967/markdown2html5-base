from __future__ import annotations

import re
from typing import ClassVar


class MarkdownToHTML:
    EMOJIS: ClassVar[dict[str, str]] = {
        "joy": "&#128514;",
        "smile": "&#128516;",
        "heart": "&#10084;&#65039;",
        "thumbsup": "&#128077;",
        "thumbsdown": "&#128078;",
        "wink": "&#128521;",
        "tada": "&#127881;",
        "rocket": "&#128640;",
        "fire": "&#128293;",
        "star": "&#11088;",
        "cry": "&#128546;",
        "thinking": "&#129300;",
        "100": "&#128175;",
        "sparkles": "&#10024;",
        "eyes": "&#128064;",
        "bulb": "&#128161;",
        "warning": "&#9888;&#65039;",
        "ok": "&#128076;",
        "check_mark": "&#10004;&#65039;",
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
        "|": "&#124;",
    }

    INLINE_RULES: ClassVar[list[tuple[str, str]]] = [
        (r"\*\*\*(.*?)\*\*\*", r"<strong><em>\1</em></strong>"),
        (r"___(.*?)___", r"<strong><em>\1</em></strong>"),
        (r"\*\*(.*?)\*\*", r"<strong>\1</strong>"),
        (r"__(.*?)__", r"<strong>\1</strong>"),
        (r"\*(.*?)\*", r"<em>\1</em>"),
        (r"_(.*?)_", r"<em>\1</em>"),
        (r"~~(.*?)~~", r"<s>\1</s>"),
        (r"==(.*?)==", r"<mark>\1</mark>"),
        (r"\~(.*?)\~", r"<sub>\1</sub>"),
        (r"\^\^(.*?)\^\^", r"<ins>\1</ins>"),
        (r"\^(.*?)\^", r"<sup>\1</sup>"),
        (r"`(.*?)`", r"<code>\1</code>"),
        (r"!\[(.*?)\]\((.*?)\)", r'<img src="\2" alt="\1">'),
        (r"\[(.*?)\]\((.*?)\)", r'<a href="\2">\1</a>'),
    ]

    TYPOGRAPHY_RULES: ClassVar[list[tuple[str, str]]] = [
        (r"\([cC]\)", "&#169;"),
        (r"\([tT][mM]\)", "&#8482;"),
        (r"\([rR]\)", "&#174;"),
        (r"\.\.\.", "&#8230;"),
        (r"---", "&#8212;"),
        (r"--", "&#8211;"),
        (r"\+/-", "&#177;"),
        (r"!=", "&#8800;"),
        (r"<=", "&#8804;"),
        (r">=", "&#8805;"),
        (r"1/2", "&#189;"),
        (r"1/4", "&#188;"),
        (r"3/4", "&#190;"),
        (r"<<", "&#171;"),
        (r">>", "&#187;"),
        (r'"([^"\n]+)"', r"&#8220;\1&#8221;"),
        (r"'([^'\n]+)'", r"&#8216;\1&#8217;"),
        (r"'", "&#8217;"),
    ]

    FOOTNOTE_REF_RE = re.compile(r"\[\^([a-zA-Z0-9]+)\]")
    FOOTNOTE_REF_HTML = (
        r'<sup id="fnref:\1"><a href="#fn:\1" class="footnote-ref">\1</a></sup>'
    )

    def _apply_footnote_refs(self, text: str) -> str:
        return self.FOOTNOTE_REF_RE.sub(self.FOOTNOTE_REF_HTML, text)

    def _replace_escapes(self, text: str) -> str:
        for char, placeholder in self.ESCAPE_CHARS.items():
            text = text.replace("\\" + char, placeholder)
        return text

    def _restore_escapes(self, text: str) -> str:
        for char, placeholder in self.ESCAPE_CHARS.items():
            clean_char = self.RESTORED_ESCAPES.get(char, char)
            text = text.replace(placeholder, clean_char)
        return text

    def convert(self, text: str) -> str:
        if not text.strip():
            return ""

        text = self._replace_escapes(text)
        text, footnotes = self._extract_footnotes(text)

        lines = text.split("\n")
        html_lines = []

        in_ul, in_ol, in_blockquote = False, False, False
        in_code_block, in_table, in_def_list = False, False, False

        paragraph_buffer = []
        code_buffer = []
        quote_buffer = []
        table_rows = []

        list_just_closed = False

        for line in lines:
            stripped = line.strip()

            # Fenced code blocks
            if stripped.startswith("```"):
                if in_code_block:
                    code_content = "\n".join(code_buffer)
                    code_content = (
                        code_content.replace("&", "&amp;")
                        .replace("<", "&lt;")
                        .replace(">", "&gt;")
                    )
                    html_lines.append(f"<pre><code>{code_content}</code></pre>")
                    code_buffer = []
                    in_code_block = False
                else:
                    self._flush_all_buffers(
                        html_lines, paragraph_buffer, quote_buffer, table_rows
                    )
                    in_code_block = True
                continue

            if in_code_block:
                code_buffer.append(line)
                continue

            # Hidden comment: [text]: #
            comment_match = re.match(r"^\[(.+)\]:\s+#\s*$", stripped)
            if comment_match:
                self._flush_all_buffers(
                    html_lines, paragraph_buffer, quote_buffer, table_rows
                )
                html_lines.append(f"<!--{comment_match.group(1)}-->")
                continue

            is_ul_item = stripped.startswith(("* ", "- "))
            is_ol_item = bool(re.match(r"^\d+\.\s+", stripped))
            is_quote_item = stripped.startswith(">")
            is_table_row = stripped.startswith("|") and stripped.endswith("|")
            is_def_desc = stripped.startswith(": ")

            heading_match = re.match(r"^(#{1,6})\s+(.*?)$", stripped)
            is_hr = bool(re.match(r"^(?:-{3,}|\*{3,}|_{3,})$", stripped))
            is_static_block = bool(heading_match or is_hr)

            # Flush paragraph buffer when container context changes
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
                    f"<p>{self._process_paragraph_breaks(paragraph_buffer)}</p>"
                )
                paragraph_buffer = []

            # Close open containers on sudden formatting breaks
            if not is_quote_item and in_blockquote:
                self._close_quote(html_lines, quote_buffer)
                quote_buffer, in_blockquote = [], False
            if not is_table_row and in_table:
                html_lines.append(self._compile_table(table_rows))
                table_rows, in_table = [], False

            # Tables
            if is_table_row:
                in_table = True
                table_rows.append(stripped)
                continue

            # Definition lists
            if is_def_desc:
                if not in_def_list:
                    in_def_list = True
                    html_lines.append("<dl>")
                    term = ""
                    if html_lines and html_lines[-1].startswith("<p>"):
                        term = html_lines.pop().replace("<p>", "").replace("</p>", "")
                    elif html_lines and not html_lines[-1].startswith("<"):
                        term = html_lines.pop()
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

            # Unordered and task lists
            if is_ul_item:
                if not in_ul:
                    self._close_containers(html_lines, ol=in_ol)
                    if in_ol:
                        list_just_closed = True
                    in_ol = False
                    html_lines.append("<ul>")
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

            # Ordered lists
            if is_ol_item:
                if not in_ol:
                    self._close_containers(html_lines, ul=in_ul)
                    if in_ul:
                        list_just_closed = True
                    in_ul = False
                    html_lines.append("<ol>")
                    in_ol = True
                content = re.sub(r"^\d+\.\s+", "", stripped)
                content = self._apply_inline_rules(content)
                html_lines.append(f"  <li>{content}</li>")
                list_just_closed = False
                continue

            if in_ul or in_ol:
                self._close_containers(html_lines, ul=in_ul, ol=in_ol)
                if in_ul or in_ol:
                    list_just_closed = True
                in_ul, in_ol = False, False

            # Blockquotes
            if is_quote_item:
                in_blockquote = True
                content = (
                    line.lstrip()[2:] if stripped.startswith("> ") else stripped[1:]
                )
                quote_buffer.append(self._apply_inline_rules(content))
                continue

            # Empty lines
            if not stripped:
                if list_just_closed:
                    html_lines.append("<!-- -->")
                    list_just_closed = False
                continue

            list_just_closed = False

            # Headings with optional custom ID
            if heading_match:
                hashes, title = heading_match.groups()
                level = len(hashes)

                id_match = re.search(r"\s+\{#([a-zA-Z0-9_-]+)\}$", title)
                id_attr = ""
                if id_match:
                    id_attr = f' id="{id_match.group(1)}"'
                    title = title[: id_match.start()]

                title = self._apply_inline_rules(title)
                html_lines.append(f"<h{level}{id_attr}>{title}</h{level}>")
                continue

            if is_hr:
                html_lines.append("<hr>")
                continue

            # Paragraphs (footnote refs are resolved after inline rules)
            paragraph_buffer.append(line)

        # Flush remaining buffers at end of document
        self._flush_all_buffers(html_lines, paragraph_buffer, quote_buffer, table_rows)
        self._close_containers(html_lines, ul=in_ul, ol=in_ol)
        if in_def_list:
            html_lines.append("</dl>")

        # Render footnote list container
        html_lines.extend(self._render_footnotes(footnotes))

        final_html = "\n".join(html_lines)
        return self._restore_escapes(final_html)

    def _render_footnotes(self, footnotes: dict[str, str]) -> list[str]:
        if not footnotes:
            return []
        lines = ['<div class="footnotes">\n  <hr>\n  <ol>']
        for fn_id, fn_text in footnotes.items():
            lines.append(
                f'    <li id="fn:{fn_id}">{fn_text} '
                f'<a href="#fnref:{fn_id}" class="footnote-backref">&uarr;</a></li>'
            )
        lines.append("  </ol>\n</div>")
        return lines

    def _close_containers(
        self, lines: list[str], ul: bool = False, ol: bool = False
    ) -> None:
        if ul:
            lines.append("</ul>")
        if ol:
            lines.append("</ol>")

    def _close_quote(self, html_lines: list[str], quote_buffer: list[str]) -> None:
        html_lines.append("<blockquote>")
        subs, curr = [], []
        for item in quote_buffer:
            if item.strip() == "":
                if curr:
                    subs.append(f"  <p>{self._process_paragraph_breaks(curr)}</p>")
                    curr = []
            else:
                curr.append(item)
        if curr:
            subs.append(f"  <p>{self._process_paragraph_breaks(curr)}</p>")
        html_lines.extend(subs)
        html_lines.append("</blockquote>")

    def _compile_table(self, rows: list[str]) -> str:
        if len(rows) < 2:
            return "\n".join(rows)

        # Find footer separator (= signs)
        footer_idx = None
        for i, row in enumerate(rows[2:], start=2):
            cells = [c.strip() for c in row.split("|")[1:-1]]
            if all(re.match(r"^:?=+:?$", c) for c in cells):
                footer_idx = i
                break

        align_row = [c.strip() for c in rows[1].split("|")[1:-1]]
        alignments = []
        for col in align_row:
            if col.startswith(":") and col.endswith(":"):
                alignments.append(' style="text-align:center;"')
            elif col.endswith(":"):
                alignments.append(' style="text-align:right;"')
            elif col.startswith(":"):
                alignments.append(' style="text-align:left;"')
            else:
                alignments.append("")

        html = ["<table>", "  <thead>", "    <tr>"]
        headers = [c.strip() for c in rows[0].split("|")[1:-1]]
        for i, h in enumerate(headers):
            align = alignments[i] if i < len(alignments) else ""
            html.append(f"      <th{align}>{self._apply_inline_rules(h)}</th>")
        html.extend(["    </tr>", "  </thead>"])

        body_rows = rows[2:footer_idx] if footer_idx else rows[2:]
        footer_rows = rows[footer_idx + 1 :] if footer_idx else []

        if body_rows:
            html.append("  <tbody>")
            for r in body_rows:
                cols = [c.strip() for c in r.split("|")[1:-1]]
                html.append("    <tr>")
                for i, c in enumerate(cols):
                    align = alignments[i] if i < len(alignments) else ""
                    html.append(f"      <td{align}>{self._apply_inline_rules(c)}</td>")
                html.append("    </tr>")
            html.append("  </tbody>")

        if footer_rows:
            html.append("  <tfoot>")
            for r in footer_rows:
                cols = [c.strip() for c in r.split("|")[1:-1]]
                html.append("    <tr>")
                for i, c in enumerate(cols):
                    align = alignments[i] if i < len(alignments) else ""
                    html.append(
                        f"      <td{align}><em>{self._apply_inline_rules(c)}</em></td>"
                    )
                html.append("    </tr>")
            html.append("  </tfoot>")

        html.append("</table>")
        return "\n".join(html)

    def _extract_footnotes(self, text: str) -> tuple[str, dict[str, str]]:
        footnotes: dict[str, str] = {}
        clean_lines = []
        for line in text.split("\n"):
            match = re.match(r"^\[\^([a-zA-Z0-9]+)\]:\s+(.*?)$", line.strip())
            if match:
                fn_id, fn_text = match.groups()
                footnotes[fn_id] = self._apply_inline_rules(fn_text)
            else:
                clean_lines.append(line)
        return "\n".join(clean_lines), footnotes

    def _process_paragraph_breaks(self, buffer_lines: list[str]) -> str:
        processed = []
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
        return self._apply_footnote_refs("\n".join(processed))

    def _flush_all_buffers(
        self,
        html: list[str],
        p_buf: list[str],
        q_buf: list[str],
        t_rows: list[str],
    ) -> None:
        if p_buf:
            html.append(f"<p>{self._process_paragraph_breaks(p_buf)}</p>")
        if q_buf:
            self._close_quote(html, q_buf)
        if t_rows:
            html.append(self._compile_table(t_rows))

    def _apply_inline_rules(self, text: str) -> str:
        # Emoji shortcodes
        for code, emoji in self.EMOJIS.items():
            text = text.replace(f":{code}:", emoji)
        # Ruby annotation
        text = re.sub(
            r"\{([^|]+)\|([^}]+)\}",
            r"<ruby>\1<rp>(</rp><rt>\2</rt><rp>)</rp></ruby>",
            text,
        )
        # Typography and math symbol replacements
        for pattern, replacement in self.TYPOGRAPHY_RULES:
            text = re.sub(pattern, replacement, text)
        # Inline text styling
        for pattern, replacement in self.INLINE_RULES:
            text = re.sub(pattern, replacement, text)
        return text
