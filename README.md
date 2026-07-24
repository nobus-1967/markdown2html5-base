# markdown2html5-base

A minimal Python 3 library that converts Markdown text into clean, semantic
HTML5 markup. Supports standard Markdown, GFM extensions, smart typography,
ruby annotations for phonetic guides, hidden comments, and table footers.

## Examples

Heading: `# Heading 1` => `<h1>Heading 1</h1>`

Bold: `**bold**` => `<strong>bold</strong>`

Italic: `*italic*` => `<em>italic</em>`

Underline: `^^underlined^^` => `<ins>underlined</ins>`

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

=> `<ul><li>Bird</li><li>Cat</li></ul>`

Blockquote:
`> Quote` => `<blockquote><p>Quote</p></blockquote>`

Code block:

```python
print('Hello, World!')
```

=> `<pre><code>print('Hello')</code></pre>`

Table with footer

```
| Product  | Qty | Price |
| :------- | :-: | ----: |
| Apples   | 2   | $3.00 |
| Bananas  | 3   | $1.50 |
| Cherries | 1   | $4.00 |
|==========|=====|=======|
| Total    | 6   | $8.50 |
```

Renders as `<table>` with `<thead>`, `<tbody>`, and `<tfoot>`.

Hidden comment:
`[hidden text]: #` => `<!--hidden text-->`

Ruby (furigana):
`{漢|かん}{字|じ}` => `<ruby>漢<rt>かん</rt></ruby><ruby>字<rt>じ</rt></ruby>`

Footnotes:

* `text[^1]` => `<sup id="fnref:1"><a href="#fn:1">1</a></sup>`
* `[^1]: body` => `<li id="fn:1">body</li>`

Typography replacements:

* `(c)` => `©`
* `(tm)` => `™`
* `1/2` => `½`
* `--` => `–`
* `...` => `…` etc.

See package's [README](./markdown2html5-base/README.md) for details.

## How it works

All markup elements used in this library are listed in
[Full Markdown Functionality Reference](./markdown2html5-base.pdf)

You can evaluate the results by creating a simple Python application to convert 
a Markdown file to an HTML5 file:

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

## Acknowledgements

Thanks to  Matt Cone for his excellent 
[Markdown Guide](https://www.markdownguide.org/)!