import pytest
from markdown2html5_base.converter import MarkdownToHTML


@pytest.fixture
def converter():
    return MarkdownToHTML()


def test_footnotes(converter):
    md_text = "Text[^1]\n\n[^1]: Footnote body"
    expected = (
        '<p>Text<sup id="fnref:1"><a href="#fn:1" class="footnote-ref">1</a></sup></p>\n'
        '<div class="footnotes">\n  <hr>\n  <ol>\n'
        '    <li id="fn:1">Footnote body <a href="#fnref:1" class="footnote-backref">&uarr;</a></li>\n'
        "  </ol>\n</div>"
    )
    assert converter.convert(md_text) == expected


def test_empty_input(converter):
    assert converter.convert("") == ""
    assert converter.convert("   \n  ") == ""


def test_headings_and_ids(converter):
    assert converter.convert("# Heading 1") == "<h1>Heading 1</h1>"
    assert converter.convert("### Title {#custom}") == '<h3 id="custom">Title</h3>'


def test_basic_inline_styles(converter):
    assert converter.convert("**bold**") == "<p><strong>bold</strong></p>"
    assert converter.convert("*italic*") == "<p><em>italic</em></p>"
    assert converter.convert("~~strikeout~~") == "<p><s>strikeout</s></p>"
    assert converter.convert("`code`") == "<p><code>code</code></p>"


def test_multiline_paragraphs_and_breaks(converter):
    md_text = "Line one\nLine two"
    assert converter.convert(md_text) == "<p>Line one\nLine two</p>"

    md_break_spaces = "Break here  \nNext line"
    assert converter.convert(md_break_spaces) == "<p>Break here<br />\nNext line</p>"

    md_break_slash = "Break here\\\nNext line"
    assert converter.convert(md_break_slash) == "<p>Break here<br />\nNext line</p>"


def test_lists_and_empty_line_comments(converter):
    md_lists = "- Item 1\n- Item 2\n\n1. First\n2. Second"
    expected = "<ul>\n  <li>Item 1</li>\n  <li>Item 2</li>\n</ul>\n<!-- -->\n<ol>\n  <li>First</li>\n  <li>Second</li>\n</ol>"
    assert converter.convert(md_lists) == expected


def test_task_lists(converter):
    assert (
        converter.convert("- [x] Done")
        == '<ul>\n  <li><input type="checkbox" checked disabled> Done</li>\n</ul>'
    )
    assert (
        converter.convert("- [ ] Todo")
        == '<ul>\n  <li><input type="checkbox" disabled> Todo</li>\n</ul>'
    )


def test_blockquotes(converter):
    md_quote = "> First para.\n>\n> Second para."
    expected = (
        "<blockquote>\n  <p>First para.</p>\n  <p>Second para.</p>\n</blockquote>"
    )
    assert converter.convert(md_quote) == expected


def test_ruby_rule(converter):
    assert (
        converter.convert("{漢|かん}")
        == "<p><ruby>漢<rp>(</rp><rt>かん</rt><rp>)</rp></ruby></p>"
    )


def test_typography_and_math(converter):
    assert converter.convert("(c) 2026...") == "<p>&#169; 2026&#8230;</p>"
    assert converter.convert("1/2 != 3/4") == "<p>&#189; &#8800; &#190;</p>"
    assert converter.convert('"Hello" and <<World>>') == (
        "<p>&#8220;Hello&#8221; and &#171;World&#187;</p>"
    )


def test_escape_characters(converter):
    assert converter.convert("\\*\\*text\\*\\*") == "<p>**text**</p>"
    assert converter.convert("1\\/2") == "<p>1/2</p>"
    assert converter.convert("\\{word|read\\}") == "<p>{word|read}</p>"


def test_emoji_shortcodes(converter):
    assert converter.convert(":joy: :heart:") == "<p>&#128514; &#10084;&#65039;</p>"
    assert converter.convert(":star:") == "<p>&#11088;</p>"
    assert (
        converter.convert(":100: and :check_mark:")
        == "<p>&#128175; and &#10004;&#65039;</p>"
    )


def test_fenced_code_blocks(converter):
    md_code = "```\n<html>\n  <body>\n```"
    expected = "<pre><code>&lt;html&gt;\n  &lt;body&gt;</code></pre>"
    assert converter.convert(md_code) == expected


def test_tables(converter):
    md_table = "| H1 | H2 |\n| :--- | ---: |\n| A | B |"
    expected = '<table>\n  <thead>\n    <tr>\n      <th style="text-align:left;">H1</th>\n      <th style="text-align:right;">H2</th>\n    </tr>\n  </thead>\n  <tbody>\n    <tr>\n      <td style="text-align:left;">A</td>\n      <td style="text-align:right;">B</td>\n    </tr>\n  </tbody>\n</table>'
    assert converter.convert(md_table) == expected


def test_tables_with_italic_footer(converter):
    md_table = "| Product | Price |\n| :--- | ---: |\n| Apples | $3.00 |\n|===|===|\n| Total | $3.00 |"
    expected = (
        '<table>\n  <thead>\n    <tr>\n      <th style="text-align:left;">Product</th>\n'
        '      <th style="text-align:right;">Price</th>\n    </tr>\n  </thead>\n'
        '  <tbody>\n    <tr>\n      <td style="text-align:left;">Apples</td>\n'
        '      <td style="text-align:right;">$3.00</td>\n    </tr>\n  </tbody>\n'
        '  <tfoot>\n    <tr>\n      <td style="text-align:left;"><em>Total</em></td>\n'
        '      <td style="text-align:right;"><em>$3.00</em></td>\n    </tr>\n  </tfoot>\n</table>'
    )
    assert converter.convert(md_table) == expected
