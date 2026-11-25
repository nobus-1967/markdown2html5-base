# markdown2html5-base

`markdown2html5-base` is a minimalist, fast, and extensible Python 3 library designed to convert Markdown text into valid, semantic HTML5 markup. It supports John Gruber’s original basic syntax, popular extended features (GFM), smart typography replacements, and a custom `ruby` rule for Asian phonetic guides (e.g., Japanese Furigana).

## 🚀 Installation

Install the library locally in editable mode from the root directory of your project:

```bash
pip install -e .
```

## 💻 CLI Usage (Terminal)

Once installed, the global command-line tool `markdown2html5-base` becomes available on your system.

### Basic Commands

* **Show help message:**

```bash
markdown2html5-base --help
```
* **Show the library version:**

```bash
markdown2html5-base -v
```
* **Convert a file and save the output:**

```bash
markdown2html5-base input.md -o output.html
```
* **Choose the print page orientation:**

```bash
markdown2html5-base input.md --page portrait -o output.html
markdown2html5-base input.md --page landscape -o output.html
```
* **Use inside Unix pipelines:**

```bash
echo "# Hello" | markdown2html5-base
```

### CSS and Print Headers

Every conversion produces a complete HTML5 document with CSS3 print styles embedded in `<head>`; there is no longer an option to emit bare, unstyled HTML. Use `--page portrait` or `--page landscape`; portrait is the default. In Python the same choice is `MarkdownToHTML().convert(text, orientation="landscape")`.

The selected stylesheet starts with a `/* Portrait PDF/Print */` or `/* Landscape PDF/Print */` comment and contains the matching `@page` margins and `@media print` rules. A script at the end of `<body>` reads `<title>`, `<meta name="author">` and `<meta name="published">` (or `date`) and sets the `--print-header` custom property used by Chromium's PDF header.

---

## 🛠️ Usage in Python Code

You can import the converter directly into your scripts:

```python
from markdown2html5_base import MarkdownToHTML

converter = MarkdownToHTML()
markdown_text = "# My Heading\nThis is text with **bold font**."

html_output = converter.convert(markdown_text)
print(html_output)

# Output: a full <!doctype html> document with embedded CSS3 print styles.
```

---

## ✨ Supported Features & Syntax

### 1. Basic Syntax

* **Headings:** `# H1` ... `###### H6`
* **Bold and Italic:** `**bold**`, `__bold__`, `*italic*`, `_italic_`. As in CommonMark, `_` does not create emphasis *inside* a word, so identifiers like `snake_case_name` and `a_b_c` are left alone. To italicise a word that contains underscores, wrap it in `*` or escape them (`snake\_case\_name`).
* **Blockquotes (with paragraph support):** `> Quote text`
* **Lists:** Unordered (`-` or `*`) and Ordered (`1.`, `2.`). Lists nest to any depth by indenting items with 2 (or 4) spaces or a tab; each level can alternate between bullets and numbers:
* **Horizontal Rules:** `---`, `***`, `___` (rendered as `<hr>`)
* **Inline Code:** `` `code` `` — HTML inside inline code is escaped automatically, so `` `<title>` `` renders as `&lt;title&gt;` and never as a real tag.
* **Links and Images:** `[Text](url)` and `![alt](url)`. A link may also carry a title — `[Text](url "Title")` → `<a href="url" title="Title">Text</a>`. The destination is taken verbatim: underscores, asterisks and quotes inside it are never treated as emphasis or typography, balanced parentheses are kept (`[T](http://e.com/a_(b))`), and a destination with spaces can be wrapped in angle brackets (`[T](<http://e.com/a b>)`). Images are wrapped in a `<figure>` element; an optional title is repeated in a `<figcaption>`: `![alt](url "Title")` → `<figure><img src="url" alt="alt" title="Title"><figcaption>Title</figcaption></figure>`.

### 2. Extended Syntax

* **Fenced Code Blocks:** HTML content inside code blocks (three backticks before and after) is escaped automatically. Fenced blocks render as `<pre><code>`. A language tag after the opening fence (e.g., `python`) is rendered as a `<div class="code-lang">python</div>` label above the `<code>` block:

```
<div class="code-lang">python</div><pre><code>print("Hello, World!")</code></pre>
```
* **Tables:** Cell alignment is configured via the delimiter row. A footer section can be added by separating it with `=` signs; footer rows render in italics:

```text
| Left | Center | Right |
| :--- | :----: | ----: |
| Text |  Text  | Text  |
|======|========|=======|
| Foot |  Foot  | Foot  |
```

This produces a `<tfoot>` section (styled in italics by the default CSS).

* **Task Lists:** `- [ ] Pending item` and `- [x] Completed item`
* **Definition Lists:**

```text
Term
: Definition of the term
```
* **Headings:** every heading gets an automatic lowercase slug ID (e.g. `# Heading 1` → `<h1 id="heading-1">`), so TOC fragment links work; `## Custom Heading Title {#custom-id}` overrides it with an explicit ID.
* **Footnotes:** Insert markers `[^1]` anywhere and define their values globally via `[^1]: Footnote body text.` Identifiers may contain letters, digits, underscores and dashes, e.g. `[^see_note_1]`.
* **Text Markers:** Strikethrough `~~text~~`, text highlight `==marker==`, underline `^^text^^`, subscript `H~2~O`, and superscript `X^2^`
* **Hidden Comments:** `[comment text]: #` renders as an invisible HTML comment `<!--comment text-->`
* **Emoji shortcodes:** `:joy:` → `😂`, `:heart:` → `❤️`, `:fire:` → `🔥`, and more — see the full table in [Emoji Shortcodes](#8-emoji-shortcodes).

### 3. Ruby Rule (Japanese Furigana)

A custom syntax for phonetic hints above kanji/characters:

* **Markdown:** `{漢|かん}{字|じ}`
* **HTML5 Output:** `<ruby>漢<rp>(</rp><rt>かん</rt><rp>)</rp></ruby><ruby>字<rp>(</rp><rt>じ</rt><rp>)</rp></ruby>`

### 4. Language Markers

Annotate blocks or inline text with a language using a valid BCP 47 tag (e.g. `de`, `fr`, `zh-Hans`).

* **Block level:** Place `{:lang} ` (with a space after it) at the very start of a line, before the Markdown tag. It renders as the global `lang` attribute on the resulting element and needs no closing marker:

```text
{:de} # Überschrift
{:fr} Un paragraphe français.
{:ru} - Пункт списка
{:de} > Ein Zitat
{:de} | Kopf  | Kopf  |
      | ----- | ----- |
      | Zelle | Zelle |
```

```html
<h1 lang="de">Überschrift</h1>
<p lang="fr">Un paragraphe français.</p>
<ul lang="ru">
  <li>Пункт списка</li>
</ul>
<blockquote lang="de">...</blockquote>
<table lang="de">...</table>
```

* **Inline level:** Wrap text with `{:lang}...{:}` to render a `<span lang="...">`:

```text
A French phrase {:fr}"L'État c'est moi"{:} is traditionally attributed to King Louis XIV of France
```

```html
<p>A French phrase <span lang="fr">&ldquo;L&lsquo;État c&rsquo;est moi&rdquo;</span> is traditionally attributed to King Louis XIV of France</p>
```

### 5. Automatic Replacements & Smart Typography

The converter formats raw text on the fly for professional typesetting, emitting HTML entities:

| Input       | Output               |
| ----------- | -------------------- |
| `(c)`       | `&copy;` (©)         |
| `(tm)`      | `&trade;` (™)        |
| `(r)`       | `&reg;` (®)          |
| `+/-`       | `&plusmn;` (±)       |
| `!=`        | `&ne;` (≠)           |
| `<=>`       | `&hArr;` (⇔)        |
| `<=`        | `&le;` (≤)           |
| `>=`        | `&ge;` (≥)           |
| `->`        | `&rarr;` (→)         |
| `<-`        | `&larr;` (←)         |
| `&uarr;`    | `&uarr;` (↑)        |
| `&darr;`    | `&darr;` (↓)         |
| `=>`        | `&rArr;` (⇒)        |
| `1/2`       | `&frac12;` (½)       |
| `1/3`       | `&frac13;` (⅓)      |
| `2/3`       | `&frac23;` (⅔)      |
| `1/4`       | `&frac14;` (¼)       |
| `3/4`       | `&frac34;` (¾)       |
| `&sol;`     | `&sol;` (/)          |
| `&bsol;`    | `&bsol;` (\)         |
| `<<`        | `&laquo;` («)        |
| `>>`        | `&raquo;` (»)        |
| `&ldquo;`   | `&ldquo;`            |
| `&rdquo;`   | `&rdquo;`            |
| `"text"`    | `&ldquo;text&rdquo;` |
| `'text'`    | `&lsquo;text&rsquo;` |
| `'`         | `&apos;` (')         |
| `---`       | `&mdash;` (—)        |
| `--`        | `&ndash;` (–)        |
| `...`       | `&hellip;` (…)       |
| `&nbsp;`    | `&nbsp;`             |

### 6. YAML Front Matter

The converter always emits a complete HTML5 document with the body content between `<body>` tags. YAML front matter between `---` lines, when present, supplies the metadata in `<head>`.

```yaml
---
lang: en
title: My Document
author: Jane Doe
description: A short description.
keywords: python, markdown, html5
published: 2026-25-11
---
```

* `lang` becomes the `<html lang="...">` attribute (a valid BCP 47 tag).
* `title` becomes the `<title>` element.
* `author`, `description`, `keywords`, and `published` become `<meta name="..." content="..." />` tags. `date` is accepted as an alias for `published`.
* A `<style>` block with CSS3 screen/print rules (fonts, headings, code blocks, tables, ruby, etc.) is always embedded in `<head>`.

```html
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="author" content="Jane Doe" />
    <meta name="description" content="A short description." />
    <meta name="keywords" content="python, markdown, html5" />
    <title>My Document</title>
    <meta name="published" content="2026-08-09" />
    <style>
      /* default viewing-friendly CSS */
    </style>
  </head>
  <body>
    ...
    <script>
      /* automatic --print-header setup */
    </script>
  </body>
</html>
```

### 7. Backslash Escaping

If you need to render a Markdown symbol literally, escape it by prefixing with a backslash: `\*` outputs a literal asterisk `*` instead of initiating italic formatting.

### 8. Emoji Shortcodes

| Shortcode      | Output              |
| -------------- | ------------------- |
| `:joy:`        | 😂                  |
| `:smile:`      | 😄                  |
| `:heart:`      | ❤️                 |
| `:thumbsup:`   | 👍                  |
| `:thumbsdown:` | 👎                  |
| `:wink:`       | 😉                  |
| `:tada:`       | 🎉                  |
| `:rocket:`     | 🚀                  |
| `:fire:`       | 🔥                  |
| `:star:`       | ⭐                  |
| `:cry:`        | 😢                  |
| `:thinking:`   | 🤔                  |
| `:100:`        | 💯                  |
| `:sparkles:`   | ✨                  |
| `:eyes:`       | 👀                  |
| `:bulb:`       | 💡                  |
| `:warning:`    | ⚠️                 |
| `:ok:`         | 👌                  |
| `:check_mark:` | ✔️                 |

### 9. CSS Styles and Print Orientation

Every output document contains one `<style>` block. It is assembled from:

* `MarkdownToHTML.DOCUMENT_CSS` — starts with `/* Base Rules */`, then base CSS3 rules for screen/WebKitGTK (`:root` variables, typography, lists, code blocks, tables, figures, ruby and CJK font stacks).
* `MarkdownToHTML.PORTRAIT_CSS` — selected by default; begins with `/* Portrait PDF/Print */` and defines A4 portrait `@page` margins plus `@media print` rules.
* `MarkdownToHTML.LANDSCAPE_CSS` — selected with `orientation="landscape"`; begins with `/* Landscape PDF/Print */` and defines A4 landscape `@page` margins plus `@media print` rules.

The orientation is validated and normalised case-insensitively. On the CLI use `--page portrait` or `--page landscape`; in Python use
`MarkdownToHTML().convert(text, orientation="landscape")`. An unknown value raises `ValueError`.

---

## 🧪 Testing

Run automatic unit tests using the `pytest` framework:

```bash
pip install pytest
pytest
```
