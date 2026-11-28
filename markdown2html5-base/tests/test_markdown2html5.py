"""End-to-end tests for the Markdown to HTML5 conversion rules."""

import subprocess
import sys

import pytest

from markdown2html5_base import __version__
from markdown2html5_base.converter import MarkdownToHTML

STYLES = MarkdownToHTML.DOCUMENT_CSS.rstrip("\n")


def body(html: str) -> str:
    """Return the document body content between the body tags."""
    if not html:
        return ""
    return html.split("  <body>\n", 1)[1].rsplit("\n  </body>", 1)[0]


@pytest.fixture
def converter():
    """Provide a fresh instance of the MarkdownToHTML converter for each test."""
    return MarkdownToHTML()


def test_footnotes(converter):
    """Verify that footnote definitions are extracted and rendered correctly at the end of the text."""
    md_text = "Text[^1]\n\n[^1]: Footnote body"
    expected = (
        '<p>Text<sup id="fnref:1"><a href="#fn:1" class="footnote-ref">1</a></sup></p>\n'
        '<div class="footnotes">\n  <hr>\n  <ol>\n'
        '    <li id="fn:1">Footnote body <a href="#fnref:1" class="footnote-backref">&uarr;</a></li>\n'
        "  </ol>\n</div>"
    )
    assert body(converter.convert(md_text)) == expected


def test_empty_input(converter):
    """Verify that completely empty strings or blank space entries safely return an empty string."""
    assert body(converter.convert("")) == ""
    assert body(converter.convert("   \n  ")) == ""


def test_headings_and_ids(converter):
    """Verify auto-generated heading anchors and optional custom layout IDs."""
    assert body(converter.convert("# Heading 1")) == '<h1 id="heading-1">Heading 1</h1>'
    assert (
        body(converter.convert("### Title {#custom}")) == '<h3 id="custom">Title</h3>'
    )
    assert (
        body(converter.convert("## 1. Headings (H1-H6)"))
        == '<h2 id="1-headings-h1-h6">1. Headings (H1-H6)</h2>'
    )


def test_basic_inline_styles(converter):
    """Verify that core markdown inline styles transform into clean HTML markup elements."""
    assert body(converter.convert("**bold**")) == "<p><strong>bold</strong></p>"
    assert body(converter.convert("*italic*")) == "<p><em>italic</em></p>"
    assert body(converter.convert("~~strikeout~~")) == "<p><s>strikeout</s></p>"
    assert body(converter.convert("`code`")) == "<p><code>code</code></p>"


def test_inline_code_escapes_html_tags(converter):
    """Verify that explicit HTML syntax characters located inside code tags are securely escaped."""
    assert body(converter.convert("`<title>`")) == "<p><code>&lt;title&gt;</code></p>"
    assert (
        body(converter.convert("`<textarea>`"))
        == "<p><code>&lt;textarea&gt;</code></p>"
    )
    assert body(converter.convert("`<style>`")) == "<p><code>&lt;style&gt;</code></p>"
    assert body(converter.convert("`<script>`")) == "<p><code>&lt;script&gt;</code></p>"
    assert body(converter.convert("`<h1>Heading</h1>`")) == (
        "<p><code>&lt;h1&gt;Heading&lt;/h1&gt;</code></p>"
    )
    assert body(converter.convert("Use `<b>bold</b>` and `<!--x-->` here")) == (
        "<p>Use <code>&lt;b&gt;bold&lt;/b&gt;</code> "
        "and <code>&lt;!--x--&gt;</code> here</p>"
    )
    assert body(converter.convert("`[text](url)` and `**not bold**`")) == (
        "<p><code>[text](url)</code> and <code>**not bold**</code></p>"
    )


def test_images(converter):
    """Verify that markdown image blocks map cleanly into standalone layout figure tags."""
    assert body(converter.convert('![Markdown](./mark_editor.png "Title")')) == (
        "<figure>\n"
        '  <img src="./mark_editor.png" alt="Markdown" title="Title">\n'
        "  <figcaption>Title</figcaption>\n"
        "</figure>"
    )
    assert body(converter.convert("![alt](src)")) == (
        '<figure>\n  <img src="src" alt="alt">\n</figure>'
    )
    assert body(converter.convert("![alt](src 'Title')")) == (
        "<figure>\n"
        '  <img src="src" alt="alt" title="Title">\n'
        "  <figcaption>Title</figcaption>\n"
        "</figure>"
    )


def test_links_keep_underscores_verbatim(converter):
    """Verify that underscores inside link text and destinations stay literal.

    The emphasis pass must never consume the `_` characters of a URL such as
    `target_x`, which previously produced a `</em>` inside the `href`.
    """
    assert body(converter.convert("[link_text](target_x)")) == (
        '<p><a href="target_x">link_text</a></p>'
    )
    assert body(converter.convert("[ext](http://e.com/a_b_c)")) == (
        '<p><a href="http://e.com/a_b_c">ext</a></p>'
    )
    assert body(converter.convert("[one](a_b) [two](c_d)")) == (
        '<p><a href="a_b">one</a> <a href="c_d">two</a></p>'
    )
    assert body(converter.convert("[Jump](#sec_one)")) == (
        '<p><a href="#sec_one">Jump</a></p>'
    )


def test_links_keep_asterisks_verbatim(converter):
    """Verify that asterisks in a link destination are not treated as emphasis markers."""
    assert body(converter.convert("[a](http://e.com/a*b*c)")) == (
        '<p><a href="http://e.com/a*b*c">a</a></p>'
    )
    assert body(converter.convert("[a](http://e.com/x_y*z)")) == (
        '<p><a href="http://e.com/x_y*z">a</a></p>'
    )


def test_underscore_emphasis_does_not_cross_link_syntax(converter):
    """Verify that an emphasis pair may span a link without corrupting its URL."""
    assert body(converter.convert("_see [link](http://e.com/a_b) now_")) == (
        '<p><em>see <a href="http://e.com/a_b">link</a> now</em></p>'
    )
    assert (
        body(converter.convert("*[x](a_b)*")) == '<p><em><a href="a_b">x</a></em></p>'
    )


def test_intraword_underscores_are_literal(converter):
    """Verify that underscores inside a word do not start or end emphasis.

    This follows the CommonMark rule for `_`, so identifiers such as
    `snake_case_name` and `a_b_c` survive conversion unchanged.
    """
    assert body(converter.convert("snake_case_name and a_b_c")) == (
        "<p>snake_case_name and a_b_c</p>"
    )
    assert body(converter.convert("_italic_ stays, snake_case_name does not")) == (
        "<p><em>italic</em> stays, snake_case_name does not</p>"
    )
    assert body(converter.convert("__bold__ and intraword__bold__here")) == (
        "<p><strong>bold</strong> and intraword__bold__here</p>"
    )
    assert body(converter.convert("a_b_c and d_e_f")) == "<p>a_b_c and d_e_f</p>"


def test_link_with_title(converter):
    """Verify that an optional link title becomes a `title` attribute, not part of the URL."""
    assert body(converter.convert('[text](http://e.com "Title")')) == (
        '<p><a href="http://e.com" title="Title">text</a></p>'
    )
    assert body(converter.convert("[text](http://e.com 'Title')")) == (
        '<p><a href="http://e.com" title="Title">text</a></p>'
    )


def test_link_with_balanced_parentheses_in_url(converter):
    """Verify that balanced parentheses inside a destination are preserved."""
    assert body(converter.convert("[text](http://e.com/a_(b))")) == (
        '<p><a href="http://e.com/a_(b)">text</a></p>'
    )


def test_link_with_angle_bracket_url(converter):
    """Verify that an angle-bracketed destination keeps spaces and is unbracketed."""
    assert body(converter.convert("[text](<http://e.com/a b>)")) == (
        '<p><a href="http://e.com/a b">text</a></p>'
    )


def test_link_label_with_nested_brackets(converter):
    """Verify that balanced brackets inside a label do not truncate it."""
    assert body(converter.convert("[text [with] brackets](url)")) == (
        '<p><a href="url">text [with] brackets</a></p>'
    )


def test_footnote_marker_with_underscore(converter):
    """Verify that footnote identifiers may contain underscores."""
    md_text = "Text[^my_note]\n\n[^my_note]: Footnote body"
    expected = (
        '<p>Text<sup id="fnref:my_note">'
        '<a href="#fn:my_note" class="footnote-ref">my_note</a></sup></p>\n'
        '<div class="footnotes">\n'
        "  <hr>\n"
        "  <ol>\n"
        '    <li id="fn:my_note">Footnote body '
        '<a href="#fnref:my_note" class="footnote-backref">&uarr;</a></li>\n'
        "  </ol>\n"
        "</div>"
    )
    assert body(converter.convert(md_text)) == expected


def test_multiline_paragraphs_and_breaks(converter):
    """Verify that standard multi-line structures and explicit line break symbols compile seamlessly."""
    md_text = "Line one\nLine two"
    assert body(converter.convert(md_text)) == "<p>Line one\nLine two</p>"

    md_break_spaces = "Break here  \nNext line"
    assert (
        body(converter.convert(md_break_spaces)) == "<p>Break here<br />\nNext line</p>"
    )

    md_break_slash = "Break here\\\nNext line"
    assert (
        body(converter.convert(md_break_slash)) == "<p>Break here<br />\nNext line</p>"
    )


def test_lists_and_empty_line_comments(converter):
    """Verify that block collections produce dedicated empty comment markers on rapid layout switches."""
    md_lists = "- Item 1\n- Item 2\n\n1. First\n2. Second"
    expected = (
        "<ul>\n  <li>Item 1</li>\n  <li>Item 2</li>\n</ul>\n"
        "<!-- -->\n"
        "<ol>\n  <li>First</li>\n  <li>Second</li>\n</ol>"
    )
    assert body(converter.convert(md_lists)) == expected


def test_task_lists(converter):
    """Verify that checklist syntax variations produce operational checkbox inputs with disabled states."""
    assert (
        body(converter.convert("- [x] Done"))
        == '<ul>\n  <li><input type="checkbox" checked disabled> Done</li>\n</ul>'
    )
    assert (
        body(converter.convert("- [ ] Todo"))
        == '<ul>\n  <li><input type="checkbox" disabled> Todo</li>\n</ul>'
    )
    assert (
        body(converter.convert("1. [x] Done"))
        == '<ol>\n  <li><input type="checkbox" checked disabled> Done</li>\n</ol>'
    )
    assert (
        body(converter.convert("1. [ ] Todo"))
        == '<ol>\n  <li><input type="checkbox" disabled> Todo</li>\n</ol>'
    )


def test_nested_list_same_type(converter):
    """Verify that an indented bullet list nests inside the parent <li>."""
    assert (
        body(
            converter.convert(
                "- Item 1\n- Item 2\n  - Subitem 1\n  - Subitem 2\n- Item 3"
            )
        )
        == "<ul>\n"
        "  <li>Item 1</li>\n"
        "  <li>Item 2\n"
        "    <ul>\n"
        "      <li>Subitem 1</li>\n"
        "      <li>Subitem 2</li>\n"
        "    </ul>\n"
        "  </li>\n"
        "  <li>Item 3</li>\n"
        "</ul>"
    )


def test_nested_list_different_type(converter):
    """Verify that an indented ordered list nests inside a bullet parent."""
    assert (
        body(
            converter.convert(
                "- Item 1\n- Item 2\n  1. Subitem 1\n  2. Subitem 2\n- Item 3"
            )
        )
        == "<ul>\n"
        "  <li>Item 1</li>\n"
        "  <li>Item 2\n"
        "    <ol>\n"
        "      <li>Subitem 1</li>\n"
        "      <li>Subitem 2</li>\n"
        "    </ol>\n"
        "  </li>\n"
        "  <li>Item 3</li>\n"
        "</ul>"
    )


def test_nested_list_mixed_types(converter):
    """Verify that alternating nested types render as sibling nested lists."""
    assert (
        body(
            converter.convert(
                "- Item 1\n- Item 2\n  1. Subitem 1\n  2. Subitem 2\n  - Subitem 3\n- Item 3"
            )
        )
        == "<ul>\n"
        "  <li>Item 1</li>\n"
        "  <li>Item 2\n"
        "    <ol>\n"
        "      <li>Subitem 1</li>\n"
        "      <li>Subitem 2</li>\n"
        "    </ol>\n"
        "    <ul>\n"
        "      <li>Subitem 3</li>\n"
        "    </ul>\n"
        "  </li>\n"
        "  <li>Item 3</li>\n"
        "</ul>"
    )


def test_nested_list_checkboxes(converter):
    """Verify that indented checklist items keep their checkbox inputs."""
    assert (
        body(
            converter.convert(
                "- Task A\n- Task B\n  - [x] Done\n  - [ ] Todo\n- Task C"
            )
        )
        == "<ul>\n"
        "  <li>Task A</li>\n"
        "  <li>Task B\n"
        "    <ul>\n"
        '      <li><input type="checkbox" checked disabled> Done</li>\n'
        '      <li><input type="checkbox" disabled> Todo</li>\n'
        "    </ul>\n"
        "  </li>\n"
        "  <li>Task C</li>\n"
        "</ul>"
    )


def test_triple_nested_list(converter):
    """Verify that a third indentation level nests a list inside a second-level <li>."""
    assert (
        body(
            converter.convert(
                "- Item 1\n"
                "- Item 2\n"
                "  - Sub 1\n"
                "    - Subsub 1\n"
                "    - Subsub 2\n"
                "  - Sub 2\n"
                "- Item 3"
            )
        )
        == "<ul>\n"
        "  <li>Item 1</li>\n"
        "  <li>Item 2\n"
        "    <ul>\n"
        "      <li>Sub 1\n"
        "        <ul>\n"
        "          <li>Subsub 1</li>\n"
        "          <li>Subsub 2</li>\n"
        "        </ul>\n"
        "      </li>\n"
        "      <li>Sub 2</li>\n"
        "    </ul>\n"
        "  </li>\n"
        "  <li>Item 3</li>\n"
        "</ul>"
    )


def test_triple_nested_list_with_type_switch(converter):
    """Verify that a deep nested list may switch type at any depth."""
    assert (
        body(
            converter.convert(
                "- Item 1\n- Item 2\n  1. Sub 1\n    - Subsub 1\n  2. Sub 2\n- Item 3"
            )
        )
        == "<ul>\n"
        "  <li>Item 1</li>\n"
        "  <li>Item 2\n"
        "    <ol>\n"
        "      <li>Sub 1\n"
        "        <ul>\n"
        "          <li>Subsub 1</li>\n"
        "        </ul>\n"
        "      </li>\n"
        "      <li>Sub 2</li>\n"
        "    </ol>\n"
        "  </li>\n"
        "  <li>Item 3</li>\n"
        "</ul>"
    )


def test_blockquotes(converter):
    """Verify that quote syntax structures bundle multi-line sequences inside blockquote wrappers."""
    md_quote = "> First para.\n>\n> Second para."
    expected = (
        "<blockquote>\n  <p>First para.</p>\n  <p>Second para.</p>\n</blockquote>"
    )
    assert body(converter.convert(md_quote)) == expected


def test_ruby_rule(converter):
    """Verify that custom shorthand markup strings produce operational semantic ruby elements."""
    assert (
        body(converter.convert("{漢|かん}"))
        == "<p><ruby>漢<rp>(</rp><rt>かん</rt><rp>)</rp></ruby></p>"
    )


def test_typography_and_math(converter):
    """Verify that complex shorthand sequences safely translate into appropriate HTML core layout entities."""
    assert body(converter.convert("(c) 2026...")) == "<p>&copy; 2026&hellip;</p>"
    assert body(converter.convert("1/2 != 3/4")) == "<p>&frac12; &ne; &frac34;</p>"
    assert body(converter.convert('"Hello" and <<World>>')) == (
        "<p>&ldquo;Hello&rdquo; and &laquo;World&raquo;</p>"
    )
    assert body(converter.convert("&sol; &bsol;")) == "<p>&sol; &bsol;</p>"
    assert body(converter.convert("a &nbsp; b")) == "<p>a &nbsp; b</p>"


def test_typography_arrows(converter):
    """Verify that structural geometric shorthand configurations generate standard numeric vector arrows."""
    assert body(converter.convert("a -> b")) == "<p>a &rarr; b</p>"
    assert body(converter.convert("a <- b")) == "<p>a &larr; b</p>"
    assert body(converter.convert("a <=> b")) == "<p>a &hArr; b</p>"
    assert body(converter.convert("a => b")) == "<p>a &rArr; b</p>"
    assert body(converter.convert("up &uarr; down &darr;")) == (
        "<p>up &uarr; down &darr;</p>"
    )


def test_front_matter_full_document(converter):
    """Verify that metadata and embedded styles form a complete document."""
    md_text = (
        "---\n"
        "lang: en\n"
        "title: My Document\n"
        "author: Jane Doe\n"
        "description: A test page\n"
        "keywords: one, two, three\n"
        "published: 2026-08-09\n"
        "---\n"
        "# Hello\n"
        "Body text."
    )
    expected = (
        "<!doctype html>\n"
        '<html lang="en">\n'
        "  <head>\n"
        '    <meta charset="utf-8" />\n'
        '    <meta name="author" content="Jane Doe" />\n'
        '    <meta name="description" content="A test page" />\n'
        '    <meta name="keywords" content="one, two, three" />\n'
        "    <title>My Document</title>\n"
        '    <meta name="published" content="2026-08-09" />\n'
        f"{STYLES}\n"
        "  </head>\n"
        "  <body>\n"
        '<h1 id="hello">Hello</h1>\n'
        "<p>Body text.</p>\n"
        "  </body>\n"
        "</html>"
    )
    assert converter.convert(md_text) == expected


def test_front_matter_quoted_values(converter):
    """Verify that quoted front matter values have their surrounding quotes stripped correctly."""
    md_text = (
        "---\ntitle: \"My Document\"\ndescription: 'A short description.'\n---\nBody"
    )
    output = converter.convert(md_text)
    assert output.startswith("<!doctype html>\n<html>\n")
    assert '<meta name="description" content="A short description." />' in output
    assert "<title>My Document</title>" in output
    assert body(output) == "<p>Body</p>"


def test_front_matter_only_lang(converter):
    """Verify that sparse front matter configures the root language attribute."""
    md_text = "---\nlang: ru\n---\n# Привет"
    output = converter.convert(md_text)
    assert output.startswith('<!doctype html>\n<html lang="ru">\n')
    assert STYLES in output
    assert body(output) == '<h1 id="привет">Привет</h1>'


def test_no_front_matter_returns_styled_document(converter):
    """Verify that plain markdown also becomes a full document with CSS."""
    output = converter.convert("# Hello")
    assert output.startswith("<!doctype html>")
    assert STYLES in output
    assert body(output) == '<h1 id="hello">Hello</h1>'


def test_include_css_option_is_removed(converter):
    """Verify that the old opt-in CSS flag is no longer part of the API."""
    for value in (True, False):
        with pytest.raises(TypeError):
            converter.convert("# Hi", include_css=value)


def test_front_matter_always_embeds_style(converter):
    """Verify that front matter always yields a document with the selected print CSS."""
    md_text = "---\nlang: en\n---\n# Hi"
    output = converter.convert(md_text)
    assert STYLES in output
    assert body(output) == '<h1 id="hi">Hi</h1>'


def test_embedded_styles_are_complete(converter):
    """Verify that both style blocks are embedded verbatim in every document."""
    output = converter.convert("# Hi")
    assert STYLES in output
    assert output.count("<style>") == 1
    assert output.count('<style media="screen">') == 1
    assert output.index("<style>") < output.index('<style media="screen">')
    assert "@page {" in output
    assert "@page landscape {" in output
    assert "@media print" in output
    assert '[data-orientation="landscape"]' in output
    assert "accent-color: var(--text-main);" in output
    assert "pre {\n  overflow-x: auto;\n}" in output
    assert "ruby {" in output
    assert "/* Portrait PDF/Print */" not in output
    assert "/* Landscape PDF/Print */" not in output


def test_portrait_orientation_uses_default_root(converter):
    """Verify that portrait output keeps the default root element untouched."""
    output = converter.convert("# Hi")
    assert output.startswith("<!doctype html>\n<html>\n")
    assert '<html lang="en"' not in output


def test_landscape_orientation_marks_root(converter):
    """Verify that landscape output selects the named print page via the root element."""
    output = converter.convert("# Hi", orientation="landscape")
    assert output.startswith(
        '<!doctype html>\n<html lang="en" data-orientation="landscape">\n'
    )


def test_landscape_preserves_front_matter_language(converter):
    """Verify that a front matter language still controls the root language attribute."""
    output = converter.convert("---\nlang: ru\n---\n# Привет", "landscape")
    assert output.startswith(
        '<!doctype html>\n<html lang="ru" data-orientation="landscape">\n'
    )


def test_orientation_aliases_and_normalisation(converter):
    """Verify case-insensitive orientation names and the page_layout alias."""
    landscape_root = '<html lang="en" data-orientation="landscape">'
    assert converter.convert("# Hi", " LANDSCAPE ").startswith(
        f"<!doctype html>\n{landscape_root}\n"
    )
    assert converter.convert("# Hi", page_layout="landscape").startswith(
        f"<!doctype html>\n{landscape_root}\n"
    )
    assert converter.convert("# Hi", " PORTRAIT ").startswith(
        "<!doctype html>\n<html>\n"
    )


def test_invalid_orientation_is_rejected(converter):
    """Verify that an unknown orientation is rejected with a helpful message."""
    with pytest.raises(ValueError, match="portrait, landscape"):
        converter.convert("# Hi", orientation="square")


def test_no_header_script(converter):
    """Verify that generated documents contain no obsolete header script."""
    output = converter.convert("# Hi")
    assert "<script>" not in output
    assert "--print-header" not in output


def test_escape_characters(converter):
    """Verify that standard backslash escape characters resolve into simple literal typography outputs."""
    assert body(converter.convert("\\*\\*text\\*\\*")) == "<p>**text**</p>"
    assert body(converter.convert("1\\/2")) == "<p>1/2</p>"
    assert body(converter.convert("\\{word|read\\}")) == "<p>{word|read}</p>"


def test_emoji_shortcodes(converter):
    """Verify that standard shortcodes are translated into their correct corresponding unicode emoji symbols."""
    assert body(converter.convert(":joy: :heart:")) == "<p>😂 ❤️</p>"
    assert body(converter.convert(":star:")) == "<p>⭐</p>"
    assert body(converter.convert(":100: and :check_mark:")) == "<p>💯 and ✔️</p>"


def test_fenced_code_blocks(converter):
    """Verify that fenced markdown code segments compile inside clean pre-formatted code block markup structures."""
    md_code = "```\n<html>\n  <body>\n```"
    expected = "<pre><code>&lt;html&gt;\n  &lt;body&gt;</code></pre>"
    assert body(converter.convert(md_code)) == expected


def test_fenced_code_block_with_language(converter):
    """Verify that explicit language designations generate an appropriately labeled structural div container block."""
    md_code = '```python\nprint("Hello, World!")\n```'
    expected = (
        '<div class="code-lang">python</div>'
        '<pre><code>print("Hello, World!")</code></pre>'
    )
    assert body(converter.convert(md_code)) == expected


def test_paragraph_before_fenced_code_not_duplicated(converter):
    """Verify that normal paragraphs preceding a code container do not leave duplicate residual lines behind."""
    assert body(converter.convert("Line\n```\ncode\n```")) == (
        "<p>Line</p>\n<pre><code>code</code></pre>"
    )


def test_tables(converter):
    """Verify that structural data data segments assemble cleanly into structured HTML semantic matrix components."""
    md_table = "| H1 | H2 |\n| :--- | ---: |\n| A | B |"
    expected = (
        "<table>\n  <thead>\n    <tr>\n"
        '      <th style="text-align:left;">H1</th>\n'
        '      <th style="text-align:right;">H2</th>\n'
        "    </tr>\n  </thead>\n  <tbody>\n    <tr>\n"
        '      <td style="text-align:left;">A</td>\n'
        '      <td style="text-align:right;">B</td>\n'
        "    </tr>\n  </tbody>\n</table>"
    )
    assert body(converter.convert(md_table)) == expected


def test_tables_with_footer(converter):
    """Verify that specifying a divider in structural table layouts produces correct layout tfoot sections."""
    md_table = "| Product | Price |\n| :--- | ---: |\n| Apples | $3.00 |\n|===|===|\n| Total | $3.00 |"
    expected = (
        '<table>\n  <thead>\n    <tr>\n      <th style="text-align:left;">Product</th>\n'
        '      <th style="text-align:right;">Price</th>\n    </tr>\n  </thead>\n'
        '  <tbody>\n    <tr>\n      <td style="text-align:left;">Apples</td>\n'
        '      <td style="text-align:right;">$3.00</td>\n    </tr>\n  </tbody>\n'
        '  <tfoot>\n    <tr>\n      <td style="text-align:left;">Total</td>\n'
        '      <td style="text-align:right;">$3.00</td>\n    </tr>\n  </tfoot>\n</table>'
    )
    assert body(converter.convert(md_table)) == expected


def test_block_language_markers(converter):
    """Verify that custom block prefix flags assign specific semantic language parameters onto root HTML components."""
    assert (
        body(converter.convert("{:de} # Heading 1"))
        == '<h1 id="heading-1" lang="de">Heading 1</h1>'
    )
    assert (
        body(converter.convert("{:fr} Text français."))
        == '<p lang="fr">Text français.</p>'
    )
    assert (
        body(converter.convert("{:de} - Item eins"))
        == '<ul lang="de">\n  <li>Item eins</li>\n</ul>'
    )
    assert (
        body(converter.convert("{:de} 1. Erstens"))
        == '<ol lang="de">\n  <li>Erstens</li>\n</ol>'
    )
    assert (
        body(converter.convert("{:de} > Zitat text"))
        == '<blockquote lang="de">\n  <p>Zitat text</p>\n</blockquote>'
    )
    assert (
        body(converter.convert("{:de} Begriff\n: Erklärung"))
        == '<dl lang="de">\n  <dt>Begriff</dt>\n  <dd>Erklärung</dd>\n</dl>'
    )


def test_block_language_marker_table(converter):
    """Verify that table structural blocks successfully inherit language attribute definitions assigned by macro prefixes."""
    md_table = "{:de} | Kopf | Kopf |\n| --- | --- |\n| Zelle | Zelle |"
    expected = (
        '<table lang="de">\n  <thead>\n    <tr>\n      <th>Kopf</th>\n'
        "      <th>Kopf</th>\n    </tr>\n  </thead>\n  <tbody>\n    <tr>\n"
        "      <td>Zelle</td>\n      <td>Zelle</td>\n    </tr>\n  </tbody>\n</table>"
    )
    assert body(converter.convert(md_table)) == expected


def test_inline_language_spans(converter):
    """Verify that embedded inline string layout configurations construct distinct span nodes with specific language properties."""
    assert body(converter.convert("Text {:fr}\"L'État c'est moi\"{:} hier.")) == (
        '<p>Text <span lang="fr">&ldquo;L&lsquo;État c&rsquo;est moi&rdquo;</span> hier.</p>'
    )
    assert body(converter.convert("{:ru} Привет {:en}world{:}!")) == (
        '<p lang="ru">Привет <span lang="en">world</span>!</p>'
    )
    assert body(converter.convert("{:de} # Titel {:en}sub{:}")) == (
        '<h1 id="titel-sub" lang="de">Titel <span lang="en">sub</span></h1>'
    )
    assert body(converter.convert("{:ja}{私|わたし}は{:}です。")) == (
        '<p><span lang="ja"><ruby>私<rp>(</rp><rt>わたし</rt><rp>)</rp></ruby>は</span>です。</p>'
    )


def test_cli_page_orientation():
    """Verify that --page portrait/landscape sets the expected root element."""
    for layout, root in (
        ("portrait", "<html>"),
        ("landscape", '<html lang="en" data-orientation="landscape">'),
    ):
        result = subprocess.run(
            [sys.executable, "-m", "markdown2html5_base.cli", "--page", layout],
            input="# Hi\n",
            text=True,
            capture_output=True,
            check=True,
        )
        assert result.stdout.startswith(f"<!doctype html>\n{root}\n")


def test_toc_links_resolve_to_heading_ids(converter):
    """Verify that fragment links in a TOC point to generated heading anchors."""
    md = (
        "## Table of Contents\n\n"
        "* [Intro](#intro)\n"
        "* [1. Headings (H1-H6)](#1-headings-h1-h6)\n\n"
        "## Intro\n\n"
        "## 1. Headings (H1-H6)\n"
    )
    output = converter.convert(md)
    assert '<a href="#intro">Intro</a>' in output
    assert '<a href="#1-headings-h1-h6">1. Headings (H1-H6)</a>' in output
    assert '<h2 id="intro">Intro</h2>' in output
    assert '<h2 id="1-headings-h1-h6">1. Headings (H1-H6)</h2>' in output


def test_package_version():
    """Verify that the published package version matches the 1.1.0 stylesheet release."""
    assert __version__ == "1.1.0"
