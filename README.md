# Limberer: Flexible document generation based on WeasyPrint, mustache templates, and Pandoc.

`limberer` is a utility for assembling markdown into documents.

## Usage

```
$ limberer create projname
$ cd projname
$ limberer build report.toml
$ open projname.pdf
```

## Features

* Markdown-based
* Consistent builds
* Automatic table of contents generation
* Mustache template hardening (disable `__` access and lambda evaluation)
* WeasyPrint hardening (restricts file access)
* Source code snippet syntax highlighting
* 2-column layouts
* Footnote support
* Image/figure support
* Markdown within HTML tables
* Flexible

## Installation

### Prerequisites

```
$ sudo apt-get install pandoc
```

***Note:*** If your distro has an older version of pandoc (e.g. 2.9.x), get it from <https://github.com/jgm/pandoc/releases/>.

```
$ wget https://github.com/jgm/pandoc/releases/download/<ver>/pandoc-<...>.deb
$ sudo dpkg -i ./pandoc-*.deb
```

### Install

```
$ pip3 install --user limberer
```

### From Source

```
$ git clone https://github.com/ChaosData/limberer && cd limberer
$ python3 -m pip install --user --upgrade pip setuptools
$ python3 -m pip install --user .
```

### Packaging

```
$ python3 -m pip install --user wheel build
$ python3 -m build --sdist --wheel .
$ python3 -m pip install --user dist/limberer-*.whl
```

### Cleaning

```
$ rm -rf ./build ./dist ./src/limberer.egg-info ./src/limberer/__pycache__
```

## Guide

`limberer` is primarily about structuring documents through the use of
"sections," which are ordered in a document's `<project>.toml` file.

These sections are based on HTML Mustache templates. For the most part, the
`section` template will be used to write document content. For such
`type = "section"` sections, the content will be sourced from a (currently)
Markdown file based on the section `name` value (`sections/<name>.md`). By
default, sections will be rendered against the `template/section.html`
template, but the template used can be changed via an `alt = "othertemplate"`
section list setting.

### Project TOML Example

```toml
title = "Example Document"
subheading = "..."
#globaloption=value
#...

authors = [
  { name = "Example Person", email = "example@example.com" },
  ...
]

sections = [
  { type = "cover" },
  { type = "toc" },
  { name = "example", type = "section" },
  { name = "example2", type = "section", sectionoption = "value" },
  ...
]
```

Additional or overriding settings or Mustache template variables can be
configured by passing additional TOML file paths into the `limberer build`
command:

```
$ limberer build report.toml stats.toml
```

### Section Templates

Out of the box, `limberer` comes with some initial section templates:

* `cover`: A title page section.
* `toc`: A table of contents section.
* `section`: The underlying template for custom sections.

Additionally, `limberer` supports the following template-like pseudo-sections:

* `appendix_start`: Subsequent sections will be treated as appendices.
* `appendix_end`: Disables the above setting; subsequent sections are not
  treated as appendices. The appendix counter will not be cleared.

### Custom Sections

Custom sections ("sections") are a mix of Markdown (and, in some cases, HTML),
with support for Mustache expressions (using the TOML configuration), where
most document content is written. A section can begin with a block of Markdown
metadata:

```markdown
---
toc_header_level: 2
columns: true
title: Example3
classes: foo bar baz
---
```

The metadata options are merged with the section entry options. Currently
supported options are the following:

* `toc_header_level`: Header level limit to use for table of contents entry
  generation.
* `columns`: Whether or not to use the 2-column format for the section.
* `title`: Section title for 2-column format.
* `classes`: List of HTML class names to apply to the section (`<article>`)
* `end_footnotes`: Footnotes will be placed at the end of the section instead
   of at/near the site of placement.

Additionally, the following options may be passed in a section entry within the
project TOML:

* `conf = "path/to/config.toml"`: This specifies a path to a TOML file that
  is loaded for the context of the section. This is useful for loading
  generated data into a section containing Mustache templating, or for reusing
  a section that is itself a "config template" combining Mustache and Markdown.
* `cont = true`: This specifies that the section's Markdown should be directly
  concatenated instead of being handled as a full section. This is useful for
  combining "config templates" together, or, more simply, just managing large
  single sections that are not intended to be divided across multiple
  `<article>` elements within the underlying HTML.

#### Tables

Tables can be written using the pipe-delimited GitHub-flavored Markdown
convention, or with HTML tables.

```markdown
| First Header  | Second Header |
| ------------- | ------------- |
| Content Cell  | Content Cell  |
| Content Cell  | Content Cell  |
```

````HTML
<table>
  <thead>
    <tr>
      <th style="width: 20%">a</th>
      <th style="width: 40%">b</th>
      <th>c</th>
      <th>d</th>
    </tr>
  </thead>
  <tbody>
    <tr><td>**Bold**</td><td>_italic_</td>
<td>
```
code block
```
</td>
<td>
* list
* of
* things
</td>
    </tr>
    <tr><td></td><td></td><td></td><td></td></tr>
    <tr><td></td><td></td><td></td><td></td></tr>
    <tr><td></td><td></td><td></td><td></td></tr>
  </tbody>
</table>
````

#### Images

A simple image can be embedded with custom CSS to place/style it:

```markdown
![](./images/test1.jpg){style="width: 30%; margin: auto; display: block;"}
```

However, for the most part, figures are a better way to embed images:

```markdown
![An example image](./images/test1.jpg){style="width: 30%; border: 1px solid red;"}
```

The figures themselves can be styled with the `figstyle` and `figclass` options:

```markdown
![Another example image](./images/test1.jpg){style="width: 1.5in" figstyle="color: red; width: 35%;" figclass="aaa bbb"}
```

Additionally, there is support for a side-by-side image-and-text in the default
layout/theme using a little HTML:

```markdown
<div class="two-col-fig">
![This is on the left](./images/test1.jpg)
<div style="width: 40%">
## A Header

Lorem ipsum dolor sit amet...
</div>
</div>
```

The order of these can also be swapped:

```markdown
<div class="two-col-fig">
<div style="width: 40%">
## A Header

Lorem ipsum dolor sit amet...
</div>
![This is on the right](./images/test1.jpg){style="width: 1.5in"}
</div>
```

#### Cross-References

Xrefs can be made through links to an element's `id`. By default, headings have
autogenerated IDs based on the heading text (e.g. `# Examplely Example` will
have an `id` of `{section}-examplely-example`. However, this can be overridden
as follows:

```markdown
## AAA{#aaah2}
```

***Note:*** The `{section}-` prefix will be applied to all `id` values other
than of the sections themselves.

To xref, any link to `#<id>` will suffice, but to style xrefs, a few options
are available in the default style/layout.

* `.xref`: A simple unstyled segment of text.

  ```
  * [xref to Example2.AAA](#example2-aaah2){.xref}
  * <a class="xref" href="#example2-aaah2">xref to Example2.AAA</a>
  ```

* `.xrefn`: This will autopopulate the target's text content.  
  ***Note:*** Be careful not to use this on elements containing large
  quantities of text via child nodes.

  ```
  * <a class="xrefn" href="#example2-aaah2"></a>
  * [](#example2-aaah2){.xrefn}
  ```

* `.xrefpg`: This will add a " on page XX".

  ```
  * <a class="xrefn xrefpg" href="#example2-aaah2"></a>
  * [](#example2-aaah2){.xrefn .xrefpg}
  ```

#### Code Blocks


````markdown
```js { lines="true" start="99" highlight="1,5" filename="HelloWorld.js" }
let j = await fetch("https://wat.wat", {
  "headers": {
    "x-test": "foo"
  }
}).then((res)=>res.json());
```
<p><center>Example Snippet of Code</center></p>

```js
let j = await fetch("https://wat.wat", {
  "headers": {
    "x-test": "foo"
  }
}).then((res)=>res.json());
```
<figure><figcaption>Example Snippet of Code with a figure prefix</figcaption></figure>
````

The following settings can be configured in the project TOML:

* `highlight` (defaults to `"monokai"`)
* `highlight_plaintext` (defaults to `"solarized-dark"`)
* `highlight_font` (defaults to `"'DejaVu Sans Mono', monospace"`)
* `highlight_style` (defaults to `"border-radius: 2px; overflow-x: auto;"`)
* `highlight_padding` (defaults to `"padding: 0.5rem 1rem 0.5rem 1rem;"`)
* `highlight_padding_lines` (defaults to `"padding: 0.25rem 0.5rem 0.25rem 0.5rem;")

#### Breaks

The following can be added to force a break.

```html
<div class="pagebreak"></div>
```

```html
<div class="columnbreak"></div>
```

#### Footnotes

Footnotes should mostly work as expected, but can fit poorly and may be better
shifted to another page.

```markdown
Hello world.[^test]

[^test]: <https://github.com/ChaosData/limberer>
```

### Theming/Styling

By default, `limberer` comes with some core styling and section templates.
It is expected that users will customize their document templates beyond what
is provided. As such, the `limberer create` command supports a `-t <path>`
option to generate a new project from a given template project directory.

Generally speaking, the styling you want to use is up to you. However, for
convenience, the CSS is organized as `core`, `style`, and `custom`. The intent
is for the `assets/core.css` to cover the main layout and functioning of the
document, the `assets/style.css` to cover group theming for consistency, and
`custom/custom.css` to be for any per-document/project styling.

## Todo List

* Support for custom Mustache-generated CSS
* Better footnotes
* Draft builds
* Partial builds of individual sections
* Support for non-Markdown sections

## FAQ

> Why?

For a litany of reasons, but if I had to go out on a limb and pick one, it
would be that LaTeX is a great typesetter, but a terrible build system.

> What!?

Greetz to asch, tanner, agrant, jblatz, and dthiel. <3
