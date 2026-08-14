# markdown2html5-base

A minimalist, fast, and extensible Python 3 library that converts Markdown text into clean, semantic HTML5 markup. Supports standard Markdown, GFM extensions, YAML front matter, smart typography, language markers, ruby annotations for phonetic guides, hidden comments, and table footers.

## Examples:

Heading: `# Heading 1` => `<h1>Heading 1</h1>`

Bold: `**bold**` => `<strong>bold</strong>`

Italic: `*italic*` => `<em>italic</em>`

Underline: `^^underlined^^` => `<u>underlined</u>`

Strikethrough: `~~deleted~~` => `<s>deleted</s>`

Highlight: `==marked==` => `<mark>marked</mark>`

Inline code: \``code`\` => `<code>code</code>`

Superscript: `X^2^` => `<sup>2</sup>` (applied inline as X<sup>2</sup>)

Subscript: `H~2~O` => `<sub>2</sub>` (applied inline as H<sub>2</sub>O)

Link: `[text](url)` => `<a href="url">text</a>`

Image: `![alt](img.png)` => `<img src="img.png" alt="alt">`

Ordered list:

```
1. First
2. Second
```

=> `<ol><li>First</li><li>Second</li></ol>`

Unordered list:

```
* Bird
* Cat
```

=>
```
<ul>
  <li>Bird</li>
  <li>Cat</li>
</ul>
```

Blockquote:
```
> Quote
```
=>
```
<blockquote>
  <p>Quote</p>
</blockquote>
```

Code block:

```python3
print('Hello')
```

=>
```
<pre>
  <code>print('Hello')</code>
</pre>
```

Table with footer

```
| Product | Qty | Price |
| :------ | :-: | ----: |
| Apples  | 2   | $3.00 |
|=========|=====|=======|
| Total   | 6   | $8.50 |
```

Renders as `<table>` with `<thead>`, `<tbody>`, and `<tfoot>`.

Hidden comment:
`[hidden text]: #` => `<!--hidden text-->`

Ruby (furigana):
`{漢|かん}{字|じ}` => `<ruby>漢<rt>かん</rt></ruby><ruby>字<rt>じ</rt></ruby>`

Footnotes:

* `text[^1]` => `<sup id="fnref:1"><a href="#fn:1">1</a></sup>`
* `[^1]: body` => `<li id="fn:1">body</li>`

Language markers (valid BCP 47 tag):

* Block (Heading): `{:de} # Überschrift` => `<h1 lang="de">Überschrift</h1>`
* Block (Paragraph): `{:fr} Un paragraphe français.` => `<p lang="fr">Un paragraphe français.</p>`
* Block (List): `{:ru} - Пункт` => `<ul lang="ru"><li>Пункт</li></ul>`
* Block (Blockquote): `{:de} > Ein Zitat` => `<blockquote lang="de"><p>Ein Zitat</p></blockquote>`
* Inline: `{:fr}"L'État c'est moi"{:}` => `<span lang="fr">&ldquo;L&lsquo;État c&rsquo;est moi&rdquo;</span>`

Typography replacements (HTML entities):

* `(c)` => `&copy;` (©)
* `(tm)` => `&trade;` (™)
* `(r)` => `&reg;` (®)
* `+/-` => `&plusmn;` (±)
* `!=` => `&ne;` (≠)
* `<=>` => `&hArr;` (⇔)
* `<=` => `&le;` (≤)
* `>=` => `&ge;` (≥)
* `->` => `&rarr;` (→)
* `<-` => `&larr;` (←)
* `:uparrow:` => `&uarr;` (↑)
* `:dnarrow:` => `&darr;` (↓)
* `=>` => `&rArr;` (⇒)
* `1/2` => `&frac12;` (½)
* `1/3` => `&frac13;` (⅓)
* `2/3` => `&frac23;` (⅔)
* `1/4` => `&frac14;` (¼)
* `3/4` => `&frac34;` (¾)
* `<<` => `&laquo;` («)
* `>>` => `&raquo;` (»)
* `"text"` => `&ldquo;text&rdquo;`
* `'text'` => `&lsquo;text&rsquo;`
* `'` => `&apos;` (')
* `---` => `&mdash;` (—)
* `--` => `&ndash;` (–)
* `...` => `&hellip;` (…)

Emoji shortcodes (HTML entities):

* `:joy:` => `&#128514;` 😂
* `:smile:` => `&#128516;` 😄
* `:heart:` => `&#10084;&#65039;` ❤️
* `:thumbsup:` => `&#128077;` 👍
* `:thumbsdown:` => `&#128078;` 👎
* `:wink:` => `&#128521;` 😉
* `:tada:` => `&#127881;` 🎉
* `:rocket:` => `&#128640;` 🚀
* `:fire:` => `&#128293;` 🔥
* `:star:` => `&#11088;` ⭐
* `:cry:` => `&#128546;` 😢
* `:thinking:` => `&#129300;` 🤔
* `:100:` => `&#128175;` 💯
* `:sparkles:` => `&#10024;` ✨
* `:eyes:` => `&#128064;` 👀
* `:bulb:` => `&#128161;` 💡
* `:warning:` => `&#9888;&#65039;` ⚠️
* `:ok:` => `&#128076;` 👌
* `:check_mark:` => `&#10004;&#65039;` ✔️

See package's [README](./markdown2html5-base/README.md) for details.

## YAML front matter

YAML front matter is an optional block at the very top of a Markdown file, delimited by `---` lines. When present, the converter emits a complete HTML5
document (with a `<!doctype html>` declaration, `<head>` metadata, and `<body>`) instead of a bare HTML fragment.

Example:

```
---
lang: en
title: My Document
author: Jane Doe
description: A short description.
keywords: python, markdown, html5
published: 2026-08-09
---
```

What each key produces:

* `lang` — the `<html lang="...">` attribute (a valid BCP 47 tag).
* `title` — the `<title>` element.
* `author`, `description`, `keywords`, and `published` — `<meta name="..." content="..." />` tags.

Resulting document:

```
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

Any other keys are ignored, and if the file has no front matter at all, the output remains a bare fragment.

## How it works

All markup elements used in this library are listed in [Full Markdown Functionality Reference](./markdown2html5-base.pdf)

You can evaluate the results by creating a simple Python application to convert a Markdown file to an HTML5 file:

```
#!/usr/bin/env python3
import sys
from markdown2html5_base import MarkdownToHTML

def main():
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <input.md> [output.html]", file=sys.stderr)
        sys.exit(1)

    with open(sys.argv[1], encoding="utf-8") as f:
        md = f.read()

    html = MarkdownToHTML().convert(md)

    if len(sys.argv) >= 3:
        with open(sys.argv[2], "w", encoding="utf-8") as f:
            f.write(html)
        print(f"Written to {sys.argv[2]}")
    else:
        print(html)

if __name__ == "__main__":
    main()
```
You can also use [markdown2pdf-base](https://github.com/nobus-1967/markdown2pdf-base) to convert a Markdown file to PDF file.

## Acknowledgements

Thanks to  Matt Cone for his excellent [Markdown Guide](https://www.markdownguide.org/)!
