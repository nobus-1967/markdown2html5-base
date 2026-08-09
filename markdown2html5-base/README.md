# markdown2html5-base

`markdown2html5-base` is a minimalist, fast, and extensible Python 3 librarydesigned to convert Markdown text into valid, semantic HTML5 markup. It supports John Gruber’s original basic syntax, popular extended features (GFM), smart typography replacements, and a custom `ruby` rule for Asian phonetic guides (e.g., Japanese Furigana).

## 🚀 Installation

Install the library locally in editable mode from the root directory of your project:

```bash
pip install -e .
```

## 💻 CLI Usage (Terminal)

Once installed, the global command-line tool `markdown2html5` becomes available on your system.

### Basic Commands

* **Show help message:**
  
  ```bash
  markdown2html5 --help
  ```
* **Convert a file and save the output:**
  
  ```bash
  markdown2html5 input.md -o output.html
  ```
* **Use inside Unix pipelines:**
  
  ```bash
  echo "# Hello" | markdown2html5
  ```

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
* **Links and Images:** `[Text](url)` and `![alt](url)`
* **Inline Code:** `` `code` ``

### 2. Extended Syntax

* **Fenced Code Blocks:** HTML content inside code blocks is escaped automatically:
  
  ```text
  <div>Some HTML code</div>
  ```
* **Tables:** Cell alignment is configured via the delimiter row. A footer section can be added by separating it with `=` signs; footer rows render in italics:

  ```text
  | Left | Center | Right |
  | :--- | :----: | ----: |
  | Text |  Text  | Text  |
  |======|========|=======|
  | Foot |  Foot  | Foot  |
  ```

  This produces a `<tfoot>` section whose cells are wrapped in `<em>` tags.
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
  A French phrase {:fr}"L'État c'est moi"{:} is traditionally attributed to King Louis XIV of France.
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
* `author`, `description`, `keywords`, and `published` become `<meta name="..." content="..." />` tags.

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

---

## 🧪 Testing

Run automatic unit tests using the `pytest` framework:

```bash
pip install pytest
pytest
```
