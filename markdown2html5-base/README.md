# markdown2html5-base

`markdown2html5-base` is a minimalist, fast, and extensible Python 3 library designed to convert Markdown text into valid, semantic HTML5 markup. It supports John Gruber’s original basic syntax, popular extended features (GFM), smart typography replacements, and a custom `ruby` rule for Asian phonetic guides.

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
* **Tables:** Cell alignment is configured via the delimiter row. A footer section can be added by separating it with `=` signs:

  ```text
  | Left | Center | Right |
  | :--- | :----: | ----: |
  | Text |  Text  | Text  |
  |=====|========|=======|
  | Foot |  Foot  | Foot  |
  ```
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
* **Emoji shortcodes:** `:joy:` 😂, `:heart:` ❤️, `:fire:` 🔥, and more.

### 3. Ruby Rule (Japanese Furigana)

A custom syntax for phonetic hints above kanji/characters:

* **Markdown:** `{漢|かん}{字|じ}`
* **HTML5 Output:** `<ruby>漢<rp>(</rp><rt>かん</rt><rp>)</rp></ruby><ruby>字<rp>(</rp><rt>じ</rt><rp>)</rp></ruby>`

### 4. Automatic Replacements & Smart Typography

The converter formats raw text on the fly for professional typesetting:

* **Quotes:** Straight quotes (`"` and `'`) change to curly open/close marks (`“ ”`, `‘ ’`).
* **Dashes:** Two hyphens `--` become an en-dash (–), and three hyphens `---` become an em-dash (—).
* **Punctuation:** Three dots `...` convert into a proper ellipsis character (…).
* **Math & Signs:** `1/2` → `½`, `3/4` → `¾`, `!=` → `≠`, `+/-` → `±`, `<=`, `>=`.
* **Guillemets and Legal Marks:** `<<` and `>>` format into guillemets (`«`, `»`), while text tokens like `(c)` or `(tm)` turn into `©` and `™`.

### 5. Backslash Escaping

If you need to render a Markdown symbol literally, escape it by prefixing with a backslash: `\*` outputs a literal asterisk `*` instead of initiating italic formatting.

---

## 🧪 Testing

Run automatic unit tests using the `pytest` framework:

```bash
pip install pytest
pytest
```
