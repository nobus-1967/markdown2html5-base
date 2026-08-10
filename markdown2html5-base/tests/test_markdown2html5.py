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


CODE_STYLE = 'style="background-color:#f0f0f0;"'
CODE_BLOCK_STYLE = (
    'style="display:block; border:1px solid #ccc; border-radius:4px; '
    'background-color:#f8f8f8; padding:10px; margin:10px 0; overflow:auto;"'
)


def test_basic_inline_styles(converter):
    assert converter.convert("**bold**") == "<p><strong>bold</strong></p>"
    assert converter.convert("*italic*") == "<p><em>italic</em></p>"
    assert converter.convert("~~strikeout~~") == "<p><s>strikeout</s></p>"
    assert converter.convert("`code`") == f"<p><code {CODE_STYLE}>code</code></p>"


def test_inline_code_escapes_html_tags(converter):
    assert (
        converter.convert("`<title>`")
        == f"<p><code {CODE_STYLE}>&lt;title&gt;</code></p>"
    )
    assert converter.convert("`<textarea>`") == (
        f"<p><code {CODE_STYLE}>&lt;textarea&gt;</code></p>"
    )
    assert (
        converter.convert("`<style>`")
        == f"<p><code {CODE_STYLE}>&lt;style&gt;</code></p>"
    )
    assert converter.convert("`<script>`") == (
        f"<p><code {CODE_STYLE}>&lt;script&gt;</code></p>"
    )
    assert converter.convert("`<h1>Heading</h1>`") == (
        f"<p><code {CODE_STYLE}>&lt;h1&gt;Heading&lt;/h1&gt;</code></p>"
    )
    assert converter.convert("Use `<b>bold</b>` and `<!--x-->` here") == (
        f"<p>Use <code {CODE_STYLE}>&lt;b&gt;bold&lt;/b&gt;</code> and "
        f"<code {CODE_STYLE}>&lt;!--x--&gt;</code> here</p>"
    )
    assert converter.convert("`[text](url)` and `**not bold**`") == (
        f"<p><code {CODE_STYLE}>[text](url)</code> and "
        f"<code {CODE_STYLE}>**not bold**</code></p>"
    )


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
    assert converter.convert("(c) 2026...") == "<p>&copy; 2026&hellip;</p>"
    assert converter.convert("1/2 != 3/4") == "<p>&frac12; &ne; &frac34;</p>"
    assert converter.convert('"Hello" and <<World>>') == (
        "<p>&ldquo;Hello&rdquo; and &laquo;World&raquo;</p>"
    )


def test_typography_arrows(converter):
    assert converter.convert("a -> b") == "<p>a &rarr; b</p>"
    assert converter.convert("a <- b") == "<p>a &larr; b</p>"
    assert converter.convert("a <=> b") == "<p>a &hArr; b</p>"
    assert converter.convert("a => b") == "<p>a &rArr; b</p>"
    assert converter.convert("up :uparrow: down :dnarrow:") == (
        "<p>up &uarr; down &darr;</p>"
    )


def test_front_matter_full_document(converter):
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
        "  </head>\n"
        "  <body>\n"
        "<h1>Hello</h1>\n"
        "<p>Body text.</p>\n"
        "  </body>\n"
        "</html>"
    )
    assert converter.convert(md_text) == expected


def test_front_matter_only_lang(converter):
    md_text = "---\nlang: ru\n---\n# Привет"
    expected = (
        "<!doctype html>\n"
        '<html lang="ru">\n'
        "  <head>\n"
        '    <meta charset="utf-8" />\n'
        "  </head>\n"
        "  <body>\n"
        "<h1>Привет</h1>\n"
        "  </body>\n"
        "</html>"
    )
    assert converter.convert(md_text) == expected


def test_no_front_matter_returns_fragment(converter):
    assert converter.convert("# Hello") == "<h1>Hello</h1>"


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
    expected = (
        f"<pre><code {CODE_BLOCK_STYLE}>&lt;html&gt;\n  &lt;body&gt;</code></pre>"
    )
    assert converter.convert(md_code) == expected


def test_paragraph_before_fenced_code_not_duplicated(converter):
    assert converter.convert("Line\n```\ncode\n```") == (
        f"<p>Line</p>\n<pre><code {CODE_BLOCK_STYLE}>code</code></pre>"
    )


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


def test_block_language_markers(converter):
    assert converter.convert("{:de} # Heading 1") == '<h1 lang="de">Heading 1</h1>'
    assert (
        converter.convert("{:fr} Text français.") == '<p lang="fr">Text français.</p>'
    )
    assert converter.convert("{:de} - Item eins") == (
        '<ul lang="de">\n  <li>Item eins</li>\n</ul>'
    )
    assert converter.convert("{:de} 1. Erstens") == (
        '<ol lang="de">\n  <li>Erstens</li>\n</ol>'
    )
    assert converter.convert("{:de} > Zitat text") == (
        '<blockquote lang="de">\n  <p>Zitat text</p>\n</blockquote>'
    )
    assert converter.convert("{:de} Begriff\n: Erklärung") == (
        '<dl lang="de">\n  <dt>Begriff</dt>\n  <dd>Erklärung</dd>\n</dl>'
    )


def test_block_language_marker_table(converter):
    md_table = "{:de} | Kopf | Kopf |\n| --- | --- |\n| Zelle | Zelle |"
    expected = (
        '<table lang="de">\n  <thead>\n    <tr>\n      <th>Kopf</th>\n'
        "      <th>Kopf</th>\n    </tr>\n  </thead>\n  <tbody>\n    <tr>\n"
        "      <td>Zelle</td>\n      <td>Zelle</td>\n    </tr>\n  </tbody>\n</table>"
    )
    assert converter.convert(md_table) == expected


def test_inline_language_spans(converter):
    assert converter.convert("Text {:fr}\"L'État c'est moi\"{:} hier.") == (
        '<p>Text <span lang="fr">&ldquo;L&lsquo;État c&rsquo;est moi&rdquo;</span> hier.</p>'
    )
    assert converter.convert("{:ru} Привет {:en}world{:}!") == (
        '<p lang="ru">Привет <span lang="en">world</span>!</p>'
    )
    assert converter.convert("{:de} # Titel {:en}sub{:}") == (
        '<h1 lang="de">Titel <span lang="en">sub</span></h1>'
    )
    assert converter.convert("{:ja}{私|わたし}は{:}です。") == (
        '<p><span lang="ja"><ruby>私<rp>(</rp><rt>わたし</rt><rp>)</rp></ruby>は</span>です。</p>'
    )
