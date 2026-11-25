# `markdown2html5-base`

# Full Markdown Functionality Reference

This reference covers all `markdown2html5-base` features.

## Table of Contents

* [Programmatic Usage](#programmatic-usage)
* [1. Headings (H1-H6)](#1-headings-h1-h6)
* [2. Inline Text Styling](#2-inline-text-styling)
* [3. Links and Images](#3-links-and-images)
* [4. Fenced Code Blocks](#4-fenced-code-blocks)
* [5. Horizontal Rules](#5-horizontal-rules)
* [6. Lists](#6-lists)
* [7. TOC (Table of Contents)](#7-toc-table-of-contents)
* [8. Blockquotes](#8-blockquotes)
* [9. Tables](#9-tables)
* [10. Definition Lists](#10-definition-lists)
* [11. Footnotes](#11-footnotes)
* [12. Language Markers](#12-language-markers)
* [13. Ruby Annotations](#13-ruby-annotations)
* [14. Emoji Shortcodes](#14-emoji-shortcodes)
* [15. Typography and Legal Marks](#15-typography-and-legal-marks)
* [16. Hard Line Breaks](#16-hard-line-breaks)
* [17. HTML Comments](#17-html-comments)
* [18. YAML Front Matter](#18-yaml-front-matter)
* [19. Backslash Escaping](#19-backslash-escaping)
* [20. Paragraphs](#20-paragraphs)
* [21. CSS Styles and Print Orientation](#21-css-styles-and-print-orientation)
* [22. Automatic PDF Header](#22-automatic-pdf-header)

## Programmatic Usage

```python
from markdown2html5_base import MarkdownToHTML
converter = MarkdownToHTML()
html = converter.convert("# Hello")  # portrait by default
landscape_html = converter.convert("# Hello", orientation="landscape")
print(html)
```

## 1. Headings (H1-H6)

| Markdown           | Output HTML          |
| ------------------ | -------------------- |
| `# Heading 1`      | `<h1>Heading 1</h1>` |
| `## Heading 2`     | `<h2>Heading 2</h2>` |
| `### Heading 3`    | `<h3>Heading 3</h3>` |
| `#### Heading 4`   | `<h4>Heading 4</h4>` |
| `##### Heading 5`  | `<h5>Heading 5</h5>` |
| `###### Heading 6` | `<h6>Heading 6</h6>` |

Custom ID: `## Section {#sec1}` => `<h2 id="sec1">Section</h2>`

## 2. Inline Text Styling

| Markdown            | Output HTML                             |
| ------------------- | --------------------------------------- |
| `***bold italic***` | `<strong><em>bold italic</em></strong>` |
| `___bold italic___` | `<strong><em>bold italic</em></strong>` |
| `**bold**`          | `<strong>bold</strong>`                 |
| `__bold__`          | `<strong>bold</strong>`                 |
| `*italic*`          | `<em>italic</em>`                       |
| `_italic_`          | `<em>italic</em>`                       |
| `~~strikethrough~~` | `<s>strikethrough</s>`                  |
| `==highlight==`     | `<mark>highlight</mark>`                |
| `~subscript~`       | `<sub>subscript</sub>`                  |
| `^^underline^^`     | `<u>underline</u>`                      |
| `^superscript^`     | `<sup>superscript</sup>`                |
| `` `code` ``        | `<code>code</code>`                     |

As in CommonMark, an underscore does not open or close emphasis inside a word, so identifiers keep their underscores: `snake_case_name` → `snake_case_name`, not `snake<em>case</em>name`. Use `*` for emphasis, or escape the underscores (`snake\_case\_name`), when the underscores must remain visible.

## 3. Links and Images

| Markdown              | Output HTML                                                                              |
| --------------------- | ---------------------------------------------------------------------------------------- |
| `[text](url)`         | `<a href="url">text</a>`                                                                 |
| `[text](url "Title")` | `<a href="url" title="Title">text</a>`                                                    |
| `![alt](src)`         | `<figure><img src="src" alt="alt"></figure>`                                             |
| `![alt](src "Title")` | `<figure><img src="src" alt="alt" title="Title"><figcaption>Title</figcaption></figure>` |

A link destination is taken verbatim and is never processed for emphasis or typography, so `[link_text](target_x)` renders as `<a href="target_x">link_text</a>`. Balanced parentheses are kept (`[text](http://e.com/a_(b))`), and a destination containing spaces can be wrapped in angle brackets (`[text](<http://e.com/a b>)`).

## 4. Fenced Code Blocks

A language tag after the opening fence (three backticks before and after the code) is rendered as a `<div class="code-lang">python</div>` label above the `<code>` element:

```html
<div class="code-lang">python</div><pre><code>def hello():
    print("Hi")</code></pre>
```

Without a language tag, the code renders plainly as `<pre><code>`.

## 5. Horizontal Rules

`---` / `***` / `___` (3+ chars) => `<hr>`

## 6. Lists

1. **Unordered:** `* Item` or `- Item` => `<ul><li>Item</li></ul>`
2. **Ordered:** `1. Item` => `<ol><li>Item</li></ol>`
3. **Task:**<br />
   `- [ ] todo` => `<ul><li><input type="checkbox" disabled> todo</li></ul>`<br />
   `1. [x] done` => `<ol><li><input type="checkbox" checked disabled> done</li></ol>`
4. **Nested:** indent an item with 2 (or 4) spaces or a tab to nest a list one level deeper. Nesting works to any depth, and each level may switch freely between bullets and numbers:

```text
- Parent
  - Child
    1. Grandchild
```

=> 

```html
<ul>
  <li>Parent
    <ul>
      <li>Child
        <ol>
          <li>Grandchild</li>
        </ol>
      </li>
    </ul>
  </li>
</ul>
```

## 7. TOC (Table of Contents)

The Table of Contents (TOC) combines the styles of Heading 2, unordered lists, and links.

```text
## Table of Contents {#toc}

- [1. Headings (H1-H6)](#1-headings-h1-h6)
- [2. Inline Text Styling](#2-inline-text-styling)
- [3. Links and Images](#3-links-and-images)
```

=>

```html
<h2 id="toc">Table of Contents</h2>
<ul>
  <li><a href="#1-headings-h1-h6">1. Headings (H1-H6)</a></li>
  <li><a href="#2-inline-text-styling">2. Inline Text Styling</a></li>
  <li><a href="#3-links-and-images">3. Links and Images</a></li>
</ul>
```

## 8. Blockquotes

`> text` => `<blockquote><p>text</p></blockquote>`: blank lines within a blockquote split into separate `<p>` tags.

## 9. Tables

Supports `<thead>`, `<tbody>`, `<tfoot>`, and alignment:

| Separator | Alignment |
| --------- | --------- |
| `:---`    | left      |
| `:---:`   | center    |
| `---:`    | right     |

Footer: a row of `=` signs below the separator columns, after the body rows, renders a `<tfoot>`.

```markdown
| Product  | Qty | Price |
| :------- | :-: | ----: |
| Apples   | 2   | $3.00 |
| Bananas  | 3   | $1.50 |
| Cherries | 1   | $4.00 |
|==========|=====|=======|
| Total    | 6   | $8.50 |
```

=>

```html
<table>
  <thead>
    <tr>
      <th style="text-align:left;">Product</th>
      <th style="text-align:center;">Qty</th>
      <th style="text-align:right;">Price</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td style="text-align:left;">Apples</td>
      <td style="text-align:center;">2</td>
      <td style="text-align:right;">$3.00</td>
    </tr>
    <tr>
      <td style="text-align:left;">Bananas</td>
      <td style="text-align:center;">3</td>
      <td style="text-align:right;">$1.50</td>
    </tr>
    <tr>
      <td style="text-align:left;">Cherries</td>
      <td style="text-align:center;">1</td>
      <td style="text-align:right;">$4.00</td>
    </tr>
  </tbody>
  <tfoot>
    <tr>
      <td style="text-align:left;">Total</td>
      <td style="text-align:center;">6</td>
      <td style="text-align:right;">$8.50</td>
    </tr>
  </tfoot>
</table>
```

## 10. Definition Lists

```markdown
Term
: Definition 1
: Definition 2
```

=>

```html
<dl>
  <dt>Term</dt>
  <dd>Definition 1</dd>
  <dd>Definition 2</dd>
</dl>
```

## 11. Footnotes

Reference: `[^1]` => `<sup id="fnref:1"><a href="#fn:1" class="footnote-ref">1</a></sup>`

Definition: `[^1]: Text` at bottom => rendered in `<div class="footnotes"><ol>...</ol></div>`

Identifiers may contain letters, digits, underscores and dashes, e.g. `[^see_note_1]`.

## 12. Language Markers

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
=>

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
=>

```html
<p>A French phrase <span lang="fr">“L‘État c’est moi”</span> is traditionally attributed to King Louis XIV of France</p>
```

## 13. Ruby Annotations

`{日本語|にほんご}` => `<ruby>日本語<rp>(</rp><rt>にほんご</rt><rp>)</rp></ruby>`

## 14. Emoji Shortcodes

* `:joy:` 😂
* `:smile:` 😄
* `:heart:` ❤️
* `:thumbsup:` 👍
* `:thumbsdown:` 👎
* `:wink:` 😉
* `:tada:` 🎉
* `:rocket:` 🚀
* `:fire:` 🔥
* `:star:` ⭐
* `:cry:` 😢
* `:thinking:` 🤔
* `:100:` 💯
* `:sparkles:` ✨
* `:eyes:` 👀
* `:bulb:` 💡
* `:warning:` ⚠️
* `:ok:` 👌
* `:check_mark:` ✔️

## 15. Typography and Legal Marks

| Name                        | Input       | HTML Output          |
| --------------------------- | ----------- | -------------------- |
| Copyright                   | `(c)`       | `&copy;`             |
| Trademark                   | `(tm)`      | `&trade;`            |
| Registered Trademark        | `(r)`       | `&reg;`              |
| Plus-Minus                  | `+/-`       | `&plusmn;`           |
| Not Equal To                | `!=`        | `&ne;`               |
| Logical Equivalence         | `<=>`       | `&hArr;`             |
| Less-Than or Equal To       | `<=`        | `&le;`               |
| Greater-Than or Equal To    | `>=`        | `&ge;`               |
| Right Arrow                 | `->`        | `&rarr;`             |
| Left Arrow                  | `<-`        | `&larr;`             |
| Up Arrow                    | `&uarr;`    | `&uarr;`             |
| Down Arrow                  | `&darr;`    | `&darr;`             |
| Logical Implication         | `=>`        | `&rArr;`             |
| Solidus (Slash)             | `&sol;`     | `&sol;`              |
| Reverse Solidus (Backslash) | `&bsol;`    | `&bsol;`             |
| One-Half                    | `1/2`       | `&frac12;`           |
| One-Third                   | `1/3`       | `&frac13;`           |
| Two-Thirds                  | `2/3`       | `&frac23;`           |
| One-Quarter                 | `1/4`       | `&frac14;`           |
| Three-Quarters              | `3/4`       | `&frac34;`           |
| Left Angle Quote            | `<<`        | `&laquo;`            |
| Right Angle Quote           | `>>`        | `&raquo;`            |
| Left Double Quote           | `&ldquo;`   | `&ldquo;`            |
| Right Double Quote          | `&rdquo;`   | `&rdquo;`            |
| Smart Double Quotes         | `"text"`    | `&ldquo;text&rdquo;` |
| Smart Single Quotes         | `'text'`    | `&lsquo;text&rsquo;` |
| Straight Apostrophe         | `'`         | `&apos;`             |
| Em Dash                     | `---`       | `&mdash;`            |
| En Dash                     | `--`        | `&ndash;`            |
| Ellipsis                    | `...`       | `&hellip;`           |
| Non-Breaking Space          | `&nbsp;`    | `&nbsp;`             |

## 16. Hard Line Breaks

End line with two spaces or backslash: `<br />`

## 17. HTML Comments

`[comment]: #` => `<!--comment-->`

## 18. YAML Front Matter

The converter always emits a complete HTML5 document with the body content between `<body>` tags. A YAML front matter block between `---` lines, when present, supplies the metadata in `<head>`. The CSS3 `<style>` block is embedded regardless of whether front matter is present.

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
* A CSS3 `<style>` block with viewing-friendly screen and print rules is embedded in `<head>`.

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
      /* CSS3 base + portrait or landscape print rules */
    </style>
  </head>
  <body>
    ...
  </body>
</html>
```

Any other keys are ignored. Documents without front matter are still complete HTML5 documents with the default CSS and the automatic header script.

## 19. Backslash Escaping

Escape any special char: `\*`, `\#`, `\[`, etc.

Escapable: \ ` * _ { } [ ] ( ) # + - . ! | ~ ^ = : < >

## 20. Paragraphs

Consecutive text lines merge into `<p>`. Blank lines separate paragraphs.

Empty line after list close => `<!-- -->` preserves whitespace.

## 21. CSS Styles and Print Orientation

Every document produced by the converter contains a single `<style>` block; emitting an unstyled HTML fragment is no longer supported. The block is assembled from three parts available as class attributes on `MarkdownToHTML`:

| Attribute       | Purpose                                                                                                                                                                  |
| ---------       | -------                                                                                                                                                                  |
| `DOCUMENT_CSS`  | Starts with `/* Base Rules */`, then base CSS3 rules for screen/WebKitGTK: custom properties, typography, lists, code blocks, tables, figures, ruby and CJK font stacks. |
| `PORTRAIT_CSS`  | Starts with `/* Portrait PDF/Print */`; A4 portrait `@page` margins and `@media print` rules.                                                                            |
| `LANDSCAPE_CSS` | Starts with `/* Landscape PDF/Print */`; A4 landscape `@page` margins and `@media print` rules.                                                                          |

The orientation name is stripped and lowercased, then validated against `("portrait", "landscape")`. An unknown value raises `ValueError`.

Python API:

```python
from markdown2html5_base import MarkdownToHTML

html = MarkdownToHTML().convert(markdown_text)                    # portrait
html = MarkdownToHTML().convert(markdown_text, "landscape")       # landscape
html = MarkdownToHTML().convert(markdown_text, page_layout="landscape")  # alias
```

CLI:

```bash
markdown2html5-base input.md --page portrait -o output.html
markdown2html5-base input.md --page landscape -o output.html
```

### `MarkdownToHTML.DOCUMENT_CSS`

```css
/* Base Rules */
:root {
  --bg-page: #ffffff;
  --bg-subtle: #f5f5f5;
  --bg-row-even: #fafafa;
  --text-main: #000000;
  --text-muted: #525252;
  --border-color: #000000;
  --border-subtle: #e0e0e0;
  --accent-mark: #ffff00;
  --font-serif: "Noto Serif", "Liberation Serif", "Times New Roman", serif;
  --font-sans: "Noto Sans", "Liberation Sans", Arial, sans-serif;
  --font-mono: "Noto Sans Mono", "Liberation Mono", monospace;
  --radius-sm: 4px;
  --space-base: 24px;
  --code-padding-x: 16px;
  --print-header: none;
}
*, *::before, *::after {
  box-sizing: border-box;
}
body {
  margin: 0;
  padding: var(--space-base) var(--space-base) var(--space-base) calc(var(--space-base) * 2);
  font-family: var(--font-serif);
  font-size: 16px;
  line-height: 1.5;
  color: var(--text-main);
  background-color: var(--bg-page);
}
h1, h2, h3, h4, h5, h6 {
  margin: 1.3em 0 0.5em;
  font-family: var(--font-sans);
  font-weight: bold;
  line-height: 1.25;
  overflow-wrap: break-word;
}
h1 { font-size: 28px; margin-top: 0; }
h2 { font-size: 24px; }
h2#toc { font-style: italic; }
h3 { font-size: 20px; }
h4 { font-size: 18px; }
h5 { font-size: 16px; }
h6 { font-size: 16px; font-style: italic; }
p {
  margin: 0.9em 0;
  overflow-wrap: break-word;
}
hr {
  height: 2px;
  margin: 24px 0;
  border: none;
  background-color: var(--border-color);
}
blockquote {
  margin: 1.2em 0;
  padding: 12px 20px;
  border-left: 4px solid var(--border-color);
  background-color: var(--bg-subtle);
  font-style: italic;
  overflow-wrap: break-word;
}
blockquote > :first-child { margin-top: 0; }
blockquote > :last-child { margin-bottom: 0; }
mark {
  padding: 2px 5px;
  border-radius: var(--radius-sm);
  background-color: var(--accent-mark);
  color: var(--text-main);
}
a:link { color: #0000cd; text-underline-offset: 2px; }
a:visited { color: #9400d3; }
a:hover, a:focus { outline: none; color: #000080; }
a:active { color: #dc143c; }
ol, ul {
  margin: 1em 0;
  padding-left: 0;
  list-style: none;
  overflow-wrap: break-word;
}
li > ol, li > ul {
  margin: 0.4em 0 0.5em;
  padding-left: 22px;
}
li > ol:last-child, li > ul:last-child {
  margin-bottom: 0;
}
ol {
  counter-reset: custom-counter;
}
li {
  position: relative;
  padding-left: 26px;
  margin-bottom: 0.4em;
  overflow-wrap: break-word;
}
li:last-child {
  margin-bottom: 0;
}
ul > li::before {
  content: "•";
  position: absolute;
  left: 8px;
  top: 0;
}
ul ul > li::before { content: "◦"; }
ul ul ul > li::before { content: "▪"; }
ul.task-list > li,
ul > li:has(input[type="checkbox"]) {
  padding-left: 4px;
}
ul.task-list > li::before,
ul > li:has(input[type="checkbox"])::before {
  display: none;
}
ol > li {
  counter-increment: custom-counter;
}
ol > li::before {
  content: counter(custom-counter) ".";
  position: absolute;
  left: 0;
  top: 0;
  font-variant-numeric: tabular-nums;
}
ol ol > li::before { content: counter(custom-counter, lower-alpha) "."; }
ol ol ol > li::before { content: counter(custom-counter, lower-roman) "."; }
ol li input[type="checkbox"],
ul li input[type="checkbox"] {
  position: static;
  display: inline-block;
  width: 15px;
  height: 15px;
  margin: 0 8px 0 0;
  vertical-align: -2px;
  accent-color: var(--text-main);
}
dl { margin: 1.2em 0; }
dt {
  margin-top: 0.9em;
  font-weight: bold;
  overflow-wrap: anywhere;
}
dd {
  margin: 0.25em 0 0;
  padding-left: 14px;
  border-left: 2px solid var(--border-subtle);
  font-style: italic;
  overflow-wrap: break-word;
}
code {
  padding: 2px 5px;
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-sm);
  background-color: var(--bg-subtle);
  font-family: var(--font-mono);
  font-size: 0.88em;
  line-height: 1;
  overflow-wrap: anywhere;
}
div.code-lang {
  display: block;
  width: fit-content;
  position: relative;
  z-index: 2;
  margin: 1.2em calc(var(--code-padding-x) + 1px) -10px auto;
  padding: 3px 10px;
  border: 1px solid var(--border-color);
  border-radius: var(--radius-sm);
  font-family: var(--font-mono);
  font-size: 0.8em;
  font-weight: bold;
  line-height: 1;
  background-color: var(--text-main);
  color: var(--bg-page);
}
pre {
  position: relative;
  z-index: 1;
  max-width: 100%;
  margin: 1.2em 0;
  padding: 16px var(--code-padding-x);
  border: 1px solid var(--border-color);
  background-color: var(--bg-subtle);
  overflow-x: auto;
}
div.code-lang + pre {
  margin-top: 0;
  padding-top: 22px;
}
pre > code {
  display: block;
  margin: 0;
  padding: 0;
  border: none;
  border-radius: 0;
  line-height: 1.45;
  background-color: transparent;
  white-space: pre;
  overflow-wrap: normal;
}
table {
  width: 100%;
  margin: 1.5em 0;
  border-collapse: collapse;
  border: 1px solid var(--border-color);
}
th, td {
  padding: 10px 14px;
  text-align: left;
  border: 1px solid var(--border-color);
  overflow-wrap: anywhere;
}
thead tr {
  background-color: var(--text-main);
  color: var(--bg-page);
}
thead th {
  font-family: var(--font-sans);
  font-weight: bold;
}

tbody tr:nth-child(even) {
  background-color: var(--bg-row-even);
}
tfoot tr {
  background-color: var(--bg-subtle);
  font-style: italic;
}
figure {
  display: block;
  margin: 1.2em 0;
}
figure img {
  display: block;
  max-width: 100%;
  height: auto;
}
figcaption {
  margin-top: 6px;
  font-size: 0.9em;
  font-style: italic;
  color: var(--text-muted);
  overflow-wrap: break-word;
}
ruby { ruby-position: over; ruby-align: space-around; }
rt { letter-spacing: 0.05em; font-size: 0.55em; white-space: nowrap; }
rp { display: none; }
span[lang="ja"] { font-family: "Noto Serif CJK JP", "Source Han Serif JP", serif; }
span[lang="zh-CN"], span[lang="zh-Hans"] { font-family: "Noto Serif CJK SC", "Source Han Serif SC", serif; }
span[lang="zh-TW"], span[lang="zh-Hant"] { font-family: "Noto Serif CJK TC", "Source Han Serif TC", serif; }
span[lang="zh-HK"] { font-family: "Noto Serif CJK HK", "Source Han Serif HK", serif; }
span[lang="ko"] { font-family: "Noto Serif CJK KR", "Source Han Serif KR", serif; }
```

### `MarkdownToHTML.PORTRAIT_CSS`

```css
/* Portrait PDF/Print */
@page {
  size: A4 portrait;
  margin: 22mm 15mm 20mm 25mm;
  @top-center {
    content: var(--print-header);
    font-family: var(--font-sans);
    font-size: 8.5pt;
    color: var(--text-muted);
    vertical-align: bottom;
    padding-bottom: 6pt;
    border-bottom: 0.5pt solid var(--border-subtle);
  }
  @bottom-center {
    content: counter(page);
    font-family: var(--font-sans);
    font-size: 8.5pt;
    color: var(--text-muted);
    vertical-align: top;
    padding-top: 6pt;
  }
}
@media print {
  * {
    -webkit-print-color-adjust: exact;
    print-color-adjust: exact;
  }
  body {
    padding: 0;
    font-size: 11pt;
    line-height: 1.45;
    color: #000000;
    background-color: #ffffff;
  }
  h1 { font-size: 20pt; }
  h2 { font-size: 17pt; }
  h3 { font-size: 14.5pt; }
  h4 { font-size: 12.5pt; }
  h5, h6 { font-size: 11pt; }
  h1, h2, h3, h4, h5, h6, dt, div.code-lang {
    break-after: avoid;
    page-break-after: avoid;
  }
  blockquote, figure, pre, tr {
    break-inside: avoid;
    page-break-inside: avoid;
  }
  p, li {
    orphans: 3;
    widows: 3;
  }
  pre {
    overflow: visible;
  }
  pre > code {
    white-space: pre-wrap;
    overflow-wrap: break-word;
  }
  thead {
    display: table-header-group;
  }
  tfoot {
    display: table-footer-group;
  }
  a:link, a:visited {
    color: #000000;
    text-decoration: underline;
    text-decoration-thickness: 1px;
  }
  a[href^="http"]::after {
    content: " (" attr(href) ")";
    font-family: var(--font-mono);
    font-size: 0.85em;
    color: var(--text-muted);
    word-break: break-all;
  }
}
```

### `MarkdownToHTML.LANDSCAPE_CSS`

```css
/* Landscape PDF/Print */
@page {
  size: A4 landscape;
  margin: 16mm 16mm 16mm 32mm;
  @top-center {
    content: var(--print-header);
    font-family: var(--font-sans);
    font-size: 8.5pt;
    color: var(--text-muted);
    vertical-align: bottom;
    padding-bottom: 5pt;
    border-bottom: 0.5pt solid var(--border-subtle);
  }
  @bottom-center {
    content: counter(page);
    font-family: var(--font-sans);
    font-size: 8.5pt;
    color: var(--text-muted);
    vertical-align: top;
    padding-top: 5pt;
  }
}
@media print {
  * {
    -webkit-print-color-adjust: exact;
    print-color-adjust: exact;
  }
  body {
    padding: 0;
    font-size: 11pt;
    line-height: 1.45;
    color: #000000;
    background-color: #ffffff;
  }
  h1 { font-size: 20pt; }
  h2 { font-size: 17pt; }
  h3 { font-size: 14.5pt; }
  h4 { font-size: 12.5pt; }
  h5, h6 { font-size: 11pt; }
  h1, h2, h3, h4, h5, h6, dt, div.code-lang {
    break-after: avoid;
    page-break-after: avoid;
  }
  blockquote, figure, pre, tr {
    break-inside: avoid;
    page-break-inside: avoid;
  }
  p, li {
    orphans: 3;
    widows: 3;
  }
  pre {
    overflow: visible;
  }
  pre > code {
    white-space: pre-wrap;
    overflow-wrap: break-word;
  }
  thead {
    display: table-header-group;
  }
  tfoot {
    display: table-footer-group;
  }
  a:link, a:visited {
    color: #000000;
    text-decoration: underline;
    text-decoration-thickness: 1px;
  }
  a[href^="http"]::after {
    content: " (" attr(href) ")";
    font-family: var(--font-mono);
    font-size: 0.85em;
    color: var(--text-muted);
    word-break: break-all;
  }
}
```

## 22. Automatic PDF Header

Every generated document ends `<body>` with the template script from the print-styles guide. It reads `<meta name="author">`, `<title>` and `<meta name="published">` (or `meta name="date"`), builds `author, title (published)` and stores it in the `--print-header` custom property used by the `@top-center` margin box. Missing metadata simply leaves the header empty.

```html
<script>
  (() => {
    const author = document.querySelector('meta[name="author"]')?.content.trim() || '';
    const title = document.title.trim() || '';
    const published = document.querySelector('meta[name="published"], meta[name="date"]')?.content.trim() || '';

    const base = [author, title].filter(Boolean).join(', ');
    const headerText = published ? (base ? `${base} (${published})` : published) : base;

    if (headerText) {
      const safeText = headerText.replace(/\\/g, '\\\\').replace(/"/g, '\\"');
      document.documentElement.style.setProperty('--print-header', `"${safeText}"`);
    }
  })();
</script>
```
