import pytest

from markdown2html5_base.converter import MarkdownToHTML


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
    assert converter.convert(md_text) == expected


def test_empty_input(converter):
    """Verify that completely empty strings or blank space entries safely return an empty string."""
    assert converter.convert("") == ""
    assert converter.convert("   \n  ") == ""


def test_headings_and_ids(converter):
    """Verify that standard block headings render correctly with optional custom layout ID attributes."""
    assert converter.convert("# Heading 1") == "<h1>Heading 1</h1>"
    assert converter.convert("### Title {#custom}") == '<h3 id="custom">Title</h3>'


def test_basic_inline_styles(converter):
    """Verify that core markdown inline styles transform into clean HTML markup elements."""
    assert converter.convert("**bold**") == "<p><strong>bold</strong></p>"
    assert converter.convert("*italic*") == "<p><em>italic</em></p>"
    assert converter.convert("~~strikeout~~") == "<p><s>strikeout</s></p>"
    assert converter.convert("`code`") == "<p><code>code</code></p>"


def test_inline_code_escapes_html_tags(converter):
    """Verify that explicit HTML syntax characters located inside code tags are securely escaped."""
    assert converter.convert("`<title>`") == "<p><code>&lt;title&gt;</code></p>"
    assert converter.convert("`<textarea>`") == "<p><code>&lt;textarea&gt;</code></p>"
    assert converter.convert("`<style>`") == "<p><code>&lt;style&gt;</code></p>"
    assert converter.convert("`<script>`") == "<p><code>&lt;script&gt;</code></p>"
    assert converter.convert("`<h1>Heading</h1>`") == (
        "<p><code>&lt;h1&gt;Heading&lt;/h1&gt;</code></p>"
    )
    assert converter.convert("Use `<b>bold</b>` and `<!--x-->` here") == (
        "<p>Use <code>&lt;b&gt;bold&lt;/b&gt;</code> "
        "and <code>&lt;!--x--&gt;</code> here</p>"
    )
    assert converter.convert("`[text](url)` and `**not bold**`") == (
        "<p><code>[text](url)</code> and <code>**not bold**</code></p>"
    )


def test_images(converter):
    """Verify that markdown image blocks map cleanly into standalone layout figure tags."""
    assert converter.convert('![Markdown](./mark_editor.png "Title")') == (
        "<figure>\n"
        '  <img src="./mark_editor.png" alt="Markdown" title="Title">\n'
        "  <figcaption>Title</figcaption>\n"
        "</figure>"
    )
    assert converter.convert("![alt](src)") == (
        '<figure>\n  <img src="src" alt="alt">\n</figure>'
    )
    assert converter.convert("![alt](src 'Title')") == (
        "<figure>\n"
        '  <img src="src" alt="alt" title="Title">\n'
        "  <figcaption>Title</figcaption>\n"
        "</figure>"
    )


def test_multiline_paragraphs_and_breaks(converter):
    """Verify that standard multi-line structures and explicit line break symbols compile seamlessly."""
    md_text = "Line one\nLine two"
    assert converter.convert(md_text) == "<p>Line one\nLine two</p>"

    md_break_spaces = "Break here  \nNext line"
    assert converter.convert(md_break_spaces) == "<p>Break here<br />\nNext line</p>"

    md_break_slash = "Break here\\\nNext line"
    assert converter.convert(md_break_slash) == "<p>Break here<br />\nNext line</p>"


def test_lists_and_empty_line_comments(converter):
    """Verify that block collections produce dedicated empty comment markers on rapid layout switches."""
    md_lists = "- Item 1\n- Item 2\n\n1. First\n2. Second"
    expected = (
        "<ul>\n  <li>Item 1</li>\n  <li>Item 2</li>\n</ul>\n"
        "<!-- -->\n"
        "<ol>\n  <li>First</li>\n  <li>Second</li>\n</ol>"
    )
    assert converter.convert(md_lists) == expected


def test_task_lists(converter):
    """Verify that checklist syntax variations produce operational checkbox inputs with disabled states."""
    assert (
        converter.convert("- [x] Done")
        == '<ul>\n  <li><input type="checkbox" checked disabled> Done</li>\n</ul>'
    )
    assert (
        converter.convert("- [ ] Todo")
        == '<ul>\n  <li><input type="checkbox" disabled> Todo</li>\n</ul>'
    )


def test_blockquotes(converter):
    """Verify that quote syntax structures bundle multi-line sequences inside blockquote wrappers."""
    md_quote = "> First para.\n>\n> Second para."
    expected = (
        "<blockquote>\n  <p>First para.</p>\n  <p>Second para.</p>\n</blockquote>"
    )
    assert converter.convert(md_quote) == expected


def test_ruby_rule(converter):
    """Verify that custom shorthand markup strings produce operational semantic ruby elements."""
    assert (
        converter.convert("{漢|かん}")
        == "<p><ruby>漢<rp>(</rp><rt>かん</rt><rp>)</rp></ruby></p>"
    )


def test_typography_and_math(converter):
    """Verify that complex shorthand sequences safely translate into appropriate HTML core layout entities."""
    assert converter.convert("(c) 2026...") == "<p>&copy; 2026&hellip;</p>"
    assert converter.convert("1/2 != 3/4") == "<p>&frac12; &ne; &frac34;</p>"
    assert converter.convert('"Hello" and <<World>>') == (
        "<p>&ldquo;Hello&rdquo; and &laquo;World&raquo;</p>"
    )
    assert converter.convert("&sol; &bsol;") == "<p>&sol; &bsol;</p>"
    assert converter.convert("a &nbsp; b") == "<p>a &nbsp; b</p>"


def test_typography_arrows(converter):
    """Verify that structural geometric shorthand configurations generate standard numeric vector arrows."""
    assert converter.convert("a -> b") == "<p>a &rarr; b</p>"
    assert converter.convert("a <- b") == "<p>a &larr; b</p>"
    assert converter.convert("a <=> b") == "<p>a &hArr; b</p>"
    assert converter.convert("a => b") == "<p>a &rArr; b</p>"
    assert converter.convert("up &uarr; down &darr;") == (
        "<p>up &uarr; down &darr;</p>"
    )


def test_front_matter_full_document(converter):
    """Verify that comprehensive meta structures construct a complete document when full styling is active."""
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
        f"    <style>\n{MarkdownToHTML.DOCUMENT_CSS}    </style>\n"
        "  </head>\n"
        "  <body>\n"
        "<h1>Hello</h1>\n"
        "<p>Body text.</p>\n"
        "  </body>\n"
        "</html>"
    )
    assert converter.convert(md_text, include_css=True) == expected


def test_front_matter_only_lang(converter):
    """Verify that sparse front matter contexts configure isolated root attribute layers correctly."""
    md_text = "---\nlang: ru\n---\n# Привет"
    expected = (
        "<!doctype html>\n"
        '<html lang="ru">\n'
        "  <head>\n"
        '    <meta charset="utf-8" />\n'
        f"    <style>\n{MarkdownToHTML.DOCUMENT_CSS}    </style>\n"
        "  </head>\n"
        "  <body>\n"
        "<h1>Привет</h1>\n"
        "  </body>\n"
        "</html>"
    )
    assert converter.convert(md_text, include_css=True) == expected


def test_no_front_matter_without_css_returns_fragment(converter):
    """Verify that a plain markdown string without front matter or CSS returns an isolated HTML fragment."""
    assert converter.convert("# Hello", include_css=False) == "<h1>Hello</h1>"


def test_no_front_matter_with_css_returns_document(converter):
    """Verify that generating an HTML document embeds the default stylesheet when CSS integration is requested."""
    output = converter.convert("# Hello", include_css=True)
    assert output.startswith("<!doctype html>")
    assert f"<style>\n{MarkdownToHTML.DOCUMENT_CSS}    </style>" in output
    assert "<h1>Hello</h1>" in output


def test_front_matter_without_css_omits_style(converter):
    """Verify that front matter configuration builds a valid structural HTML file but leaves out inline styles."""
    md_text = "---\nlang: en\n---\n# Hi"
    output = converter.convert(md_text, include_css=False)
    assert "<style>" not in output
    assert output.startswith("<!doctype html>")


def test_front_matter_with_css_embeds_style(converter):
    """Verify that providing valid front matter properties alongside an active CSS request embeds the document style block."""
    md_text = "---\nlang: en\n---\n# Hi"
    output = converter.convert(md_text, include_css=True)
    assert f"<style>\n{MarkdownToHTML.DOCUMENT_CSS}    </style>" in output


def test_escape_characters(converter):
    """Verify that standard backslash escape characters resolve into simple literal typography outputs."""
    assert converter.convert("\\*\\*text\\*\\*") == "<p>**text**</p>"
    assert converter.convert("1\\/2") == "<p>1/2</p>"
    assert converter.convert("\\{word|read\\}") == "<p>{word|read}</p>"


def test_emoji_shortcodes(converter):
    """Verify that standard shortcodes are translated into their correct corresponding unicode emoji symbols."""
    assert converter.convert(":joy: :heart:") == "<p>😂 ❤️</p>"
    assert converter.convert(":star:") == "<p>⭐</p>"
    assert converter.convert(":100: and :check_mark:") == "<p>💯 and ✔️</p>"


def test_fenced_code_blocks(converter):
    """Verify that fenced markdown code segments compile inside clean pre-formatted code block markup structures."""
    md_code = "```\n<html>\n  <body>\n```"
    expected = "<pre><code>&lt;html&gt;\n  &lt;body&gt;</code></pre>"
    assert converter.convert(md_code) == expected


def test_fenced_code_block_with_language(converter):
    """Verify that explicit language designations generate an appropriately labeled structural div container block."""
    md_code = '```python\nprint("Hello, World!")\n```'
    expected = (
        '<div class="code-lang">&sol;python&sol;</div>'
        '<pre><code>print("Hello, World!")</code></pre>'
    )
    assert converter.convert(md_code) == expected


def test_paragraph_before_fenced_code_not_duplicated(converter):
    """Verify that normal paragraphs preceding a code container do not leave duplicate residual lines behind."""
    assert converter.convert("Line\n```\ncode\n```") == (
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
    assert converter.convert(md_table) == expected


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
    assert converter.convert(md_table) == expected


def test_block_language_markers(converter):
    """Verify that custom block prefix flags assign specific semantic language parameters onto root HTML components."""
    assert converter.convert("{:de} # Heading 1") == '<h1 lang="de">Heading 1</h1>'
    assert (
        converter.convert("{:fr} Text français.") == '<p lang="fr">Text français.</p>'
    )
    assert (
        converter.convert("{:de} - Item eins")
        == '<ul lang="de">\n  <li>Item eins</li>\n</ul>'
    )
    assert (
        converter.convert("{:de} 1. Erstens")
        == '<ol lang="de">\n  <li>Erstens</li>\n</ol>'
    )
    assert (
        converter.convert("{:de} > Zitat text")
        == '<blockquote lang="de">\n  <p>Zitat text</p>\n</blockquote>'
    )
    assert (
        converter.convert("{:de} Begriff\n: Erklärung")
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
    assert converter.convert(md_table) == expected


def test_inline_language_spans(converter):
    """Verify that embedded inline string layout configurations construct distinct span nodes with specific language properties."""
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
