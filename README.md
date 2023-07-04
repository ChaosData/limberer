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
$ sudo apt-get install pandoc highlight
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

### Project TOML

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
  { name = "example", type = "section", title = "Example" },
  { name = "example2", type = "section", title = "Example2", sectionoption = "value" },
  ...
]
```

### Sections

Sections are a mix of Markdown (and, in some cases, HTML), where most document
content is written. A section can begin with a block of Markdown metadata:

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

* Draft builds
* Partial builds of individual sections
* Support for non-Markdown sections

## FAQ

> Why?

For a litany of reasons, but if I had to go out on a limb and pick one, it
would be that LaTeX is a great typesetter, but a terrible build system.

> What!?

Greetz to asch, tanner, agrant, jblatz, and dthiel. <3
