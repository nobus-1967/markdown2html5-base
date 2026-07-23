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

```python3
print('Hello')
```

=> `<pre><code>print('Hello')</code></pre>`

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

Typography replacements:

* `(c)` => `©`
* `(tm)` => `™`
* `1/2` => `½`
* `--` => `–`
* `...` => `…` etc.

See package's [README](./markdown2html5-base/README.md) for details.

All markup elements used in this library are listed in 
[Full Markdown Functionality Reference](./markdown2html5-base.pdf)

## Acknowledgements

Thanks to  Matt Cone for his excellent 
[Markdown Guide](https://www.markdownguide.org/)!