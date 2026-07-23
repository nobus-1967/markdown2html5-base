import re

class MarkdownToHTML:
    def __init__(self):
        # Emoji shortcodes dictionary
        self.emojis = {
            "joy": "😂", "smile": "😄", "heart": "❤️", "thumbsup": "👍",
            "thumbsdown": "👎", "wink": "😉", "tada": "🎉", "rocket": "🚀",
            "fire": "🔥", "star": "⭐", "cry": "😭", "thinking": "🤔"
        }

        # Escape characters map for backslash escaping
        self.escape_chars = {
            "\\": "%%ESC_BACKSLASH%%",
            "`": "%%ESC_BACKTICK%%",
            "*": "%%ESC_ASTERISK%%",
            "_": "%%ESC_UNDERSCORE%%",
            "{": "%%ESC_LBRACE%%",
            "}": "%%ESC_RBRACE%%",
            "[": "%%ESC_LBRACKET%%",
            "]": "%%ESC_RBRACKET%%",
            "(": "%%ESC_LPAREN%%",
            ")": "%%ESC_RPAREN%%",
            "#": "%%ESC_HASH%%",
            "+": "%%ESC_PLUS%%",
            "-": "%%ESC_MINUS%%",
            ".": "%%ESC_DOT%%",
            "!": "%%ESC_EXCLAMATION%%",
            "|": "%%ESC_PIPE%%",
            "~": "%%ESC_TILDE%%",
            "^": "%%ESC_CARET%%",
            "=": "%%ESC_EQUAL%%",
            ":": "%%ESC_COLON%%",
            "<": "%%ESC_LT%%",
            ">": "%%ESC_GT%%"
        }

        # Basic and extended inline regex rules
        self.inline_rules = [
            (r'\*\*\*(.*?)\*\*\*', r'<strong><em>\1</em></strong>'),
            (r'___(.*?)___', r'<strong><em>\1</em></strong>'),
            (r'\*\*(.*?)\*\*', r'<strong>\1</strong>'),
            (r'__(.*?)__', r'<strong>\1</strong>'),
            (r'\*(.*?)\*', r'<em>\1</em>'),
            (r'_(.*?)_', r'<em>\1</em>'),
            (r'~~(.*?)~~', r'<s>\1</s>'),
            (r'==(.*?)==', r'<mark>\1</mark>'),
            (r'\~(.*?)\~', r'<sub>\1</sub>'),
            (r'\^\^(.*?)\^\^', r'<ins>\1</ins>'),
            (r'\^(.*?)\^', r'<sup>\1</sup>'),
            (r'`(.*?)`', r'<code>\1</code>'),
            (r'!\[(.*?)\]\((.*?)\)', r'<img src="\2" alt="\1">'),
            (r'\[(.*?)\]\((.*?)\)', r'<a href="\2">\1</a>'),
        ]

        # Automatic typography, legal marks, and math symbol replacements
        self.typography_rules = [
            (r'\([cC]\)', '©'),
            (r'\([tT][mM]\)', '™'),
            (r'\([rR]\)', '®'),
            (r'\.\.\.', '…'),
            (r'---', '—'),
            (r'--', '–'),
            (r'\+/-', '±'),
            (r'!=', '≠'),
            (r'<=', '≤'),
            (r'>=', '≥'),
            (r'1/2', '½'),
            (r'1/4', '¼'),
            (r'3/4', '¾'),
            (r'<<', '«'),
            (r'>>', '»'),
            (r'"([^"\n]+)"', r'“\1”'),
            (r'"', '”'),
            (r'\'([^\'\n]+)\'', r'‘\1’'),
            (r'\'', '’'),
        ]

        # Block element rules
        self.block_rules = [
            (r'^#{6}\s+(.*?)$', r'<h6>\1</h6>'),
            (r'^#{5}\s+(.*?)$', r'<h5>\1</h5>'),
            (r'^#{4}\s+(.*?)$', r'<h4>\1</h4>'),
            (r'^#{3}\s+(.*?)$', r'<h3>\1</h3>'),
            (r'^#{2}\s+(.*?)$', r'<h2>\1</h2>'),
            (r'^#{1}\s+(.*?)$', r'<h1>\1</h1>'),
            (r'^(?:-{3,}|\*{3,}|_{3,})$', r'<hr>'),
        ]

    def _replace_escapes(self, text: str) -> str:
        # Step 1: Replace escaped characters with temporary placeholders
        text = text.replace(r'\\', self.escape_chars['\\'])
        for char, placeholder in self.escape_chars.items():
            if char != '\\':
                text = text.replace('\\' + char, placeholder)
        return text

    def _restore_escapes(self, text: str) -> str:
        # Step 2: Restore escaped characters to their clean versions
        for char, placeholder in self.escape_chars.items():
            clean_char = char
            if char == '<': clean_char = '&lt;'
            elif char == '>': clean_char = '&gt;'
            elif char == '|': clean_char = '&#124;'
            text = text.replace(placeholder, clean_char)
        return text

    def convert(self, text: str) -> str:
        if not text.strip():
            return ""

        # Isolate escaped characters
        text = self._replace_escapes(text)

        # Preprocess and extract footnote definitions
        text, footnotes = self._extract_footnotes(text)

        lines = text.split('\n')
        html_lines = []
        
        # State variables for block containers
        in_ul, in_ol, in_blockquote = False, False, False
        in_code_block, in_table, in_def_list = False, False, False
        
        # Line buffers for multi-block content
        paragraph_buffer = []
        code_buffer = []
        quote_buffer = []
        table_rows = []
        
        # Track list closing state for empty line comments
        list_just_closed = False

        for line in lines:
            stripped = line.strip()

            # Process Fenced Code Blocks
            if stripped.startswith('```'):
                if in_code_block:
                    code_content = '\n'.join(code_buffer)
                    code_content = code_content.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
                    html_lines.append(f"<pre><code>{code_content}</code></pre>")
                    code_buffer = []
                    in_code_block = False
                else:
                    self._flush_all_buffers(html_lines, paragraph_buffer, quote_buffer, table_rows)
                    in_code_block = True
                continue

            if in_code_block:
                code_buffer.append(line)
                continue

            # Hidden comment: [text]: #
            comment_match = re.match(r'^\[(.+)\]:\s+#\s*$', stripped)
            if comment_match:
                self._flush_all_buffers(html_lines, paragraph_buffer, quote_buffer, table_rows)
                html_lines.append(f'<!--{comment_match.group(1)}-->')
                continue

            # Identify line content types
            is_ul_item = stripped.startswith('* ') or stripped.startswith('- ')
            is_ol_item = bool(re.match(r'^\d+\.\s+', stripped))
            is_quote_item = stripped.startswith('>')
            is_table_row = stripped.startswith('|') and stripped.endswith('|')
            is_def_desc = stripped.startswith(': ')

            is_static_block = False
            heading_match = re.match(r'^(#{1,6})\s+(.*?)$', stripped)
            is_hr = bool(re.match(r'^(?:-{3,}|\*{3,}|_{3,})$', stripped))
            if heading_match or is_hr:
                is_static_block = True

            # Flush paragraph buffers when container context changes
            if is_ul_item or is_ol_item or is_quote_item or is_static_block or is_table_row or is_def_desc or not stripped:
                if paragraph_buffer:
                    html_lines.append(f"<p>{self._process_paragraph_breaks(paragraph_buffer)}</p>")
                    paragraph_buffer = []

            # Close open containers on sudden formatting breaks
            if not is_quote_item and in_blockquote:
                self._close_quote(html_lines, quote_buffer)
                quote_buffer, in_blockquote = [], False
            if not is_table_row and in_table:
                html_lines.append(self._compile_table(table_rows))
                table_rows, in_table = [], False

            # Process Markdown Tables
            if is_table_row:
                in_table = True
                table_rows.append(stripped)
                continue

            # Process Definition Lists
            if is_def_desc:
                if not in_def_list:
                    in_def_list = True
                    html_lines.append('<dl>')
                    term = ""
                    if html_lines and html_lines[-1].startswith('<p>'):
                        term = html_lines.pop().replace('<p>', '').replace('</p>', '')
                    elif html_lines and not html_lines[-1].startswith('<'):
                        term = html_lines.pop()
                    if term:
                        html_lines.append(f"  <dt>{self._apply_inline_rules(term)}</dt>")
                
                desc_content = stripped[2:]
                html_lines.append(f"  <dd>{self._apply_inline_rules(desc_content)}</dd>")
                continue
            
            if in_def_list and not is_def_desc and stripped:
                html_lines.append('</dl>')
                in_def_list = False

            # Process Unordered and Task Lists
            if is_ul_item:
                if not in_ul:
                    self._close_containers(html_lines, ol=in_ol)
                    if in_ol: list_just_closed = True
                    in_ol = False
                    html_lines.append('<ul>')
                    in_ul = True
                
                content = stripped[2:]
                if content.startswith('[x] ') or content.startswith('[X] '):
                    content = '<input type="checkbox" checked disabled> ' + self._apply_inline_rules(content[4:])
                elif content.startswith('[ ] '):
                    content = '<input type="checkbox" disabled> ' + self._apply_inline_rules(content[4:])
                else:
                    content = self._apply_inline_rules(content)
                    
                html_lines.append(f'  <li>{content}</li>')
                list_just_closed = False
                continue

            # Process Ordered Lists
            if is_ol_item:
                if not in_ol:
                    self._close_containers(html_lines, ul=in_ul)
                    if in_ul: list_just_closed = True
                    in_ul = False
                    html_lines.append('<ol>')
                    in_ol = True
                content = re.sub(r'^\d+\.\s+', '', stripped)
                content = self._apply_inline_rules(content)
                html_lines.append(f'  <li>{content}</li>')
                list_just_closed = False
                continue

            if in_ul or in_ol:
                self._close_containers(html_lines, ul=in_ul, ol=in_ol)
                if in_ul or in_ol: list_just_closed = True
                in_ul, in_ol = False, False

            # Process Blockquotes
            if is_quote_item:
                in_blockquote = True
                content = line.lstrip()[2:] if stripped.startswith('> ') else stripped[1:]
                quote_buffer.append(self._apply_inline_rules(content))
                continue

            # Empty lines
            if not stripped:
                if list_just_closed:
                    html_lines.append('<!-- -->')
                    list_just_closed = False
                continue

            list_just_closed = False

            # Process Headings and Horizontal Rules
            if heading_match:
                hashes, title = heading_match.groups()
                level = len(hashes)
                
                id_match = re.search(r'\s+\{#([a-zA-Z0-9_-]+)\}$', title)
                id_attr = ""
                if id_match:
                    id_attr = f' id="{id_match.group(1)}"'
                    title = title[:id_match.start()]
                
                title = self._apply_inline_rules(title)
                html_lines.append(f'<h{level}{id_attr}>{title}</h{level}>')
                continue

            if is_hr:
                html_lines.append('<hr>')
                continue

            # Paragraphs and footnote reference tags
            line_processed = re.sub(r'\[\^([a-zA-Z0-9]+)\]', r'<sup id="fnref:\1"><a href="#fn:\1" class="footnote-ref">\1</a></sup>', line)
            paragraph_buffer.append(line_processed)

        # Flush remaining buffers at end of document
        self._flush_all_buffers(html_lines, paragraph_buffer, quote_buffer, table_rows)
        self._close_containers(html_lines, ul=in_ul, ol=in_ol)
        if in_def_list: html_lines.append('</dl>')

        # Render footnote list container
        if footnotes:
            html_lines.append('<div class="footnotes">\n  <hr>\n  <ol>')
            for fn_id, fn_text in footnotes.items():
                html_lines.append(f'    <li id="fn:{fn_id}">{fn_text} <a href="#fnref:{fn_id}" class="footnote-backref">&#8617;</a></li>')
            html_lines.append('  </ol>\n</div>')

        # Restore escaped values and finalize output
        final_html = '\n'.join(html_lines)
        return self._restore_escapes(final_html)

    def _close_containers(self, lines, ul=False, ol=False):
        if ul: lines.append('</ul>')
        if ol: lines.append('</ol>')

    def _close_quote(self, html_lines, quote_buffer):
        html_lines.append('<blockquote>')
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
        html_lines.append('</blockquote>')

    def _compile_table(self, rows) -> str:
        if len(rows) < 2: return '\n'.join(rows)

        # Find footer separator (= signs)
        footer_idx = None
        for i, row in enumerate(rows[2:], start=2):
            cells = [c.strip() for c in row.split('|')[1:-1]]
            if all(re.match(r'^:?=+:?$', c) for c in cells):
                footer_idx = i
                break

        align_row = [c.strip() for c in rows[1].split('|')[1:-1]]
        alignments = []
        for col in align_row:
            if col.startswith(':') and col.endswith(':'): alignments.append(' style="text-align:center;"')
            elif col.endswith(':'): alignments.append(' style="text-align:right;"')
            elif col.startswith(':'): alignments.append(' style="text-align:left;"')
            else: alignments.append('')

        html = ["<table>", "  <thead>", "    <tr>"]
        headers = [c.strip() for c in rows[0].split('|')[1:-1]]
        for i, h in enumerate(headers):
            align = alignments[i] if i < len(alignments) else ''
            html.append(f'      <th{align}>{self._apply_inline_rules(h)}</th>')
        html.extend(["    </tr>", "  </thead>"])

        body_rows = rows[2:footer_idx] if footer_idx else rows[2:]
        footer_rows = rows[footer_idx+1:] if footer_idx else []

        if body_rows:
            html.append("  <tbody>")
            for r in body_rows:
                cols = [c.strip() for c in r.split('|')[1:-1]]
                html.append("    <tr>")
                for i, c in enumerate(cols):
                    align = alignments[i] if i < len(alignments) else ''
                    html.append(f'      <td{align}>{self._apply_inline_rules(c)}</td>')
                html.append("    </tr>")
            html.append("  </tbody>")

        if footer_rows:
            html.append("  <tfoot>")
            for r in footer_rows:
                cols = [c.strip() for c in r.split('|')[1:-1]]
                html.append("    <tr>")
                for i, c in enumerate(cols):
                    align = alignments[i] if i < len(alignments) else ''
                    html.append(f'      <td{align}>{self._apply_inline_rules(c)}</td>')
                html.append("    </tr>")
            html.append("  </tfoot>")

        html.append("</table>")
        return '\n'.join(html)

    def _extract_footnotes(self, text: str):
        footnotes = {}
        clean_lines = []
        for line in text.split('\n'):
            match = re.match(r'^\[\^([a-zA-Z0-9]+)\]:\s+(.*?)$', line.strip())
            if match:
                fn_id, fn_text = match.groups()
                footnotes[fn_id] = self._apply_inline_rules(fn_text)
            else:
                clean_lines.append(line)
        return '\n'.join(clean_lines), footnotes

    def _process_paragraph_breaks(self, buffer_lines) -> str:
        processed = []
        for line in buffer_lines:
            has_break = line.endswith('  ') or line.endswith('\\')
            clean = line[:-2] if line.endswith('  ') else (line[:-1] if line.endswith('\\') else line)
            inline = self._apply_inline_rules(clean.strip())
            if has_break: inline += '<br />'
            processed.append(inline)
        return '\n'.join(processed)

    def _flush_all_buffers(self, html, p_buf, q_buf, t_rows):
        if p_buf: html.append(f"<p>{self._process_paragraph_breaks(p_buf)}</p>")
        if q_buf: self._close_quote(html, q_buf)
        if t_rows: html.append(self._compile_table(t_rows))

    def _apply_inline_rules(self, text: str) -> str:
        # Step 1: Emoji replacements
        for code, emoji in self.emojis.items():
            text = text.replace(f":{code}:", emoji)
        # Step 2: Ruby annotation
        text = re.sub(r'\{([^|]+)\|([^}]+)\}', r'<ruby>\1<rp>(</rp><rt>\2</rt><rp>)</rp></ruby>', text)
        # Step 3: Typography and math symbol replacements
        for pattern, replacement in self.typography_rules:
            text = re.sub(pattern, replacement, text)
        # Step 4: Inline text styling
        for pattern, replacement in self.inline_rules:
            text = re.sub(pattern, replacement, text)
        return text
