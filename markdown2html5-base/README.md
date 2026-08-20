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
* **Embed the default viewing-friendly CSS in the output document:**

```bash
markdown2html5-base --css input.md -o output.html
```
* **Use inside Unix pipelines:**

```bash
echo "# Hello" | markdown2html5-base
```

### Embedding the Default CSS

By default the CLI produces a bare HTML fragment (or a document without a `<style>` block). Pass `--css` to embed the viewing-friendly stylesheet
in `<head>` and wrap the output in a full HTML document:

```bash
markdown2html5-base --css input.md -o output.html
```

The embedded CSS covers fonts, headings, code blocks, tables, blockquotes, links, highlight marks, CJK font stacks, ruby annotations, and horizontal
rules. `--css` works regardless of YAML front matter.
The same behaviour is available in Python via `MarkdownToHTML().convert(text, include_css=True)`.

---

## 🛠️ Usage in Python Code

You can import the converter directly into your scripts:

```python
from markdown2html5_base import MarkdownToHTML

converter = MarkdownToHTML()
markdown_text = "# My Heading\nThis is text with **bold font**."

html_output = converter.convert(markdown_text)
print(html_output)

# Output: <h1>My Heading</h1>\n<p>This is text with <strong>bold font</strong>.</p>
```

---

## ✨ Supported Features & Syntax

### 1. Basic Syntax

* **Headings:** `# H1` ... `###### H6`
* **Bold and Italic:** `**bold**`, `__bold__`, `*italic*`, `_italic_`
* **Blockquotes (with paragraph support):** `> Quote text`
* **Lists:** Unordered (`-` or `*`) and Ordered (`1.`, `2.`)
* **Horizontal Rules:** `---`, `***`, `___` (rendered as `<hr>`)
* **Inline Code:** `` `code` `` — HTML inside inline code is escaped automatically, so `` `<title>` `` renders as `&lt;title&gt;` and never as a real tag.
* **Links and Images:** `[Text](url)` and `![alt](url)`. Images support an optional title: `![alt](url "Title")` → `<img src="url" alt="alt" title="Title">`.

### 2. Extended Syntax

* **Fenced Code Blocks:** HTML content inside code blocks (three backticks before and after) is escaped automatically. Fenced blocks render as `<pre><code>`. A language tag after the opening fence (e.g., `python`) is rendered as a `<div class="code-lang">&sol;python&sol;</div>` label above the `<code>` block:

```
<div class="code-lang">&sol;python&sol;</div><pre><code>print("Hello, World!")</code></pre>
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
* **Headings with custom IDs:** `## Custom Heading Title {#custom-id}`
* **Footnotes:** Insert markers `[^1]` anywhere and define their values globally via `[^1]: Footnote body text.`
* **Text Markers:** Strikethrough `~~text~~`, text highlight `==marker==`, underline `^^text^^`, subscript `H~2~O`, and superscript `X^2^`
* **Hidden Comments:** `[comment text]: #` renders as an invisible HTML comment `<!--comment text-->`
* **Emoji shortcodes:** `:joy:` → `&#128514;` (😂), `:heart:` → `&#10084;&#65039;` (❤️), `:fire:` → `&#128293;` (🔥), and more — see the full table in [Emoji Shortcodes](#8-emoji-shortcodes).

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
| `:uparrow:` |  `&uarr;` (↑)        |
| `:dnarrow:` | `&darr;` (↓)         |
| `=>`        | `&rArr;` (⇒)        |
| `1/2`       | `&frac12;` (½)       |
| `1/3`       | `&frac13;` (⅓)      |
| `2/3`       | `&frac23;` (⅔)      |
| `1/4`       | `&frac14;` (¼)       |
| `3/4`       | `&frac34;` (¾)       |
| `:slash:`   | `&sol;` (/)          |
| `:bslash:`  | `&bsol;` (\)         |
| `<<`        | `&laquo;` («)        |
| `>>`        | `&raquo;` (»)        |
| `"text"`    | `&ldquo;text&rdquo;` |
| `'text'`    | `&lsquo;text&rsquo;` |
| `'`         | `&apos;` (')         |
| `---`       | `&mdash;` (—)        |
| `--`        | `&ndash;` (–)        |
| `...`       | `&hellip;` (…)       |

### 6. YAML Front Matter

If the file begins with a YAML front matter block between `---` lines, the converter emits a complete HTML5 document with the metadata in `<head>` and the body content between `<body>` tags. Without front matter, the output stays a bare HTML fragment.

```yaml
---
lang: en
title: My Document
author: Jane Doe
description: A short description.
keywords: python, markdown, html5
published: 2026-08-09
---
```

* `lang` becomes the `<html lang="...">` attribute (a valid BCP 47 tag).
* `title` becomes the `<title>` element.
* `author`, `description`, `keywords`, and `published` become `<meta name="..." content="..." />` tags. `date` is accepted as an alias for `published`.
* A default `<style>` block with viewing-friendly CSS (fonts, headings, code blocks, tables, ruby, etc.) is embedded in `<head>` when `--css` is passed on the CLI or `include_css=True` is used in Python.

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
  </body>
</html>
```

### 7. Backslash Escaping

If you need to render a Markdown symbol literally, escape it by prefixing with a backslash: `\*` outputs a literal asterisk `*` instead of initiating italic formatting.

### 8. Emoji Shortcodes

| Shortcode      | Output                  |
| -------------- | ----------------------- |
| `:joy:`        | `&#128514;` (😂)        |
| `:smile:`      | `&#128516;` (😄)        |
| `:heart:`      | `&#10084;&#65039;` (❤️) |
| `:thumbsup:`   | `&#128077;` (👍)        |
| `:thumbsdown:` | `&#128078;` (👎)        |
| `:wink:`       | `&#128521;` (😉)        |
| `:tada:`       | `&#127881;` (🎉)        |
| `:rocket:`     | `&#128640;` (🚀)        |
| `:fire:`       | `&#128293;` (🔥)        |
| `:star:`       | `&#11088;` (⭐)         |
| `:cry:`        | `&#128546;` (😢)        |
| `:thinking:`   | `&#129300;` (🤔)        |
| `:100:`        | `&#128175;` (💯)        |
| `:sparkles:`   | `&#10024;` (✨)         |
| `:eyes:`       | `&#128064;` (👀)        |
| `:bulb:`       | `&#128161;` (💡)        |
| `:warning:`    | `&#9888;&#65039;` (⚠️)  |
| `:ok:`         | `&#128076;` (👌)        |
| `:check_mark:` | `&#10004;&#65039;` (✔️) |

### 9. CSS Styles

The converter can embed a default `<style>` block in `<head>` (with `--css` or `include_css=True`) that provides viewing-friendly styling, regardless of YAML front matter.
Full list of CSS rules (available in code as `MarkdownToHTML.DOCUMENT_CSS`):

```
body {
  padding: 20px;
  font-family:
    "Noto Serif",
    "Liberation Serif",
    "Times New Roman",
    Times,
    serif;
  font-size: 18px;
  line-height: 1.4;
  color: #000000;
}
h1, h2, h3, h4, h5, h6 {
  margin-top: 1.2em;
  margin-bottom: 0.6em;
  font-family:
    "Noto Sans",
    "Liberation Sans",
    Arial,
    sans-serif;
  font-weight: bold;
}
h1 { font-size: 32px; }
h2 { font-size: 28px; }
h3 { font-size: 24px; }
h4 { font-size: 20px; }
h5 { font-size: 18px; }
h6 {
  font-size: 18px;
  font-style: italic;
}
hr {
  height: 4px;
  margin: 20px 0;
  border: none;
  background-color: #000000;
}
li {
  position: relative;
  padding-left: 20px;
}
dt { font-weight: bold; }
dd {
  position: relative;
  margin-left: 0;
  padding-left: 20px;
  font-style: italic;
}
blockquote {
  margin-left: 0;
  padding-left: 20px;
  border-left: 8px solid #f5f5f5;
}
mark {
  padding: 0 2px;
  border-radius: 4px;
  background-color: #ffff00;
}
a:link { color: #0000cd; }
a:visited { color: #9400d3; }
a:hover, a:focus {
  outline: none;
  color: #000080;
}
a:active { color: #dc143c; }
code {
  padding: 2px 4px;
  border-radius: 4px;
  font-family:
    "Noto Sans Mono",
    "Liberation Mono",
    "Courier New",
    Courier,
    monospace;
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
  font-family:
    "Noto Sans Mono",
    "Liberation Mono",
    "Courier New",
    Courier,
    monospace;
  font-size: 0.9em;
  line-height: 1;
  background-color: #000000;
  color: #ffffff;
  font-weight: bold;
}
table {
  margin: 20px 0;
  border-collapse: collapse;
}
th, td {
  padding: 10px 12px;
  border: 1px solid #000000;
}
th { font-weight: bold; }
thead tr {
  background-color: #000000;
  color: #ffffff;
}
tfoot tr {
  background-color: #f5f5f5;
  font-style: italic;
}
ruby { ruby-position: over; }
rt {
  letter-spacing: 0.05em;
  font-size: 0.55em;
  line-break: strict;
}
rp { display: none; }
span[lang="ja"] {
  font-family:
    "Noto Serif CJK JP",
    "Source Han Serif JP",
    "源ノ明朝",
    "Source Han Serif",
    "Hiragino Mincho ProN",
    "Hiragino Mincho Pro",
    "IPAexMincho",
    "IPAMincho",
    "MS PMincho",
    "MS Mincho",
    serif;
}
span[lang="zh-CN"], span[lang="zh-Hans"] {
  font-family:
    "Noto Serif CJK SC",
    "Source Han Serif SC",
    "思源宋体",
    "Source Han Serif CN",
    "Source Han Serif",
    "Songti SC",
    "FandolSong",
    "WenQuanYi Bitmap Song",
    "SimSun",
    serif;
}
span[lang="zh-TW"], span[lang="zh-Hant"] {
  font-family:
    "Noto Serif CJK TC",
    "Source Han Serif TC",
    "思源宋體",
    "Source Han Serif TW",
    "Source Han Serif",
    "Apple LiSung",
    "LiSong Pro",
    "HanaMinA",
    "PMingLiU",
    "MingLiU",
    serif;
}
span[lang="zh-HK"] {
  font-family:
    "Noto Serif CJK HK",
    "Source Han Serif HK",
    "思源宋體 香港",
    "思源宋體",
    "Source Han Serif",
    "Apple LiSung",
    "LiSong Pro",
    "HanaMinA",
    "MingLiU_HKSCS",
    "PMingLiU",
    "MingLiU",
    serif;
}
span[lang="ko"] {
  font-family:
    "Noto Serif CJK KR",
    "Source Han Serif KR",
    "본명조",
    "Source Han Serif",
    "AppleMyungjo",
    "UnBatang",
    "은바탕",
    "Batang",
    serif;
}
```
---

## 🧪 Testing

Run automatic unit tests using the `pytest` framework:

```bash
pip install pytest
pytest
```
