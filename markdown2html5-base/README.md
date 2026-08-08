# markdown2html5-base

`markdown2html5-base` is a minimalist, fast, and extensible Python 3 library designed to convert Markdown text into valid, semantic HTML5 markup. It supports John Gruber’s original basic syntax, popular extended features (GFM), smart typography replacements, and a custom `ruby` rule for Asian phonetic guides (e.g., Japanese Furigana).

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
  |=====|========|=======|
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
* **Emoji shortcodes:** `:joy:` → `&#128514;` (😂), `:heart:` → `&#10084;&#65039;` (❤️), `:fire:` → `&#128293;` (🔥), and more — see the full table in [Emoji Shortcodes](#6-emoji-shortcodes).

### 3. Ruby Rule (Japanese Furigana)

A custom syntax for phonetic hints above kanji/characters:

* **Markdown:** `{漢|かん}{字|じ}`
* **HTML5 Output:** `<ruby>漢<rp>(</rp><rt>かん</rt><rp>)</rp></ruby><ruby>字<rp>(</rp><rt>じ</rt><rp>)</rp></ruby>`

### 4. Automatic Replacements & Smart Typography

The converter formats raw text on the fly for professional typesetting, emitting HTML entities:

| Input   | Output             |
| ------- | ------------------ |
| `(c)`   | `&#169;` (©)       |
| `(tm)`  | `&#8482;` (™)      |
| `(r)`   | `&#174;` (®)       |
| `...`   | `&#8230;` (…)      |
| `---`   | `&#8212;` (—)      |
| `--`    | `&#8211;` (–)      |
| `+/-`   | `&#177;` (±)       |
| `!=`    | `&#8800;` (≠)      |
| `<=`    | `&#8804;` (≤)      |
| `>=`    | `&#8805;` (≥)      |
| `1/2`   | `&#189;` (½)       |
| `1/4`   | `&#188;` (¼)       |
| `3/4`   | `&#190;` (¾)       |
| `<<`    | `&#171;` («)       |
| `>>`    | `&#187;` (»)       |
| `"text"`| `&#8220;text&#8221;` |
| `'text'`| `&#8216;text&#8217;` |
| `'`     | `&#8217;` (’)      |

### 5. Backslash Escaping

If you need to render a Markdown symbol literally, escape it by prefixing with a backslash: `\*` outputs a literal asterisk `*` instead of initiating italic formatting.

### 6. Emoji Shortcodes

| Shortcode     | Output                 |
| ------------- | ---------------------- |
| `:joy:`       | `&#128514;` (😂)       |
| `:smile:`     | `&#128516;` (😄)       |
| `:heart:`     | `&#10084;&#65039;` (❤️)|
| `:thumbsup:`  | `&#128077;` (👍)       |
| `:thumbsdown:`| `&#128078;` (👎)       |
| `:wink:`      | `&#128521;` (😉)       |
| `:tada:`      | `&#127881;` (🎉)       |
| `:rocket:`    | `&#128640;` (🚀)       |
| `:fire:`      | `&#128293;` (🔥)       |
| `:star:`      | `&#11088;` (⭐)        |
| `:cry:`       | `&#128546;` (😢)       |
| `:thinking:`  | `&#129300;` (🤔)       |
| `:100:`       | `&#128175;` (💯)       |
| `:sparkles:`  | `&#10024;` (✨)        |
| `:eyes:`      | `&#128064;` (👀)       |
| `:bulb:`      | `&#128161;` (💡)       |
| `:warning:`   | `&#9888;&#65039;` (⚠️) |
| `:ok:`        | `&#128076;` (👌)       |
| `:check_mark:`| `&#10004;&#65039;` (✔️)|

---

## 🧪 Testing

Run automatic unit tests using the `pytest` framework:

```bash
pip install pytest
pytest
```
