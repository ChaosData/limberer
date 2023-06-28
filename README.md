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

Coming soon...

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

## FAQ

> Why?

For a litany of reasons, but if I had to go out on a limb and pick one, it
would be that LaTeX is a great typesetter, but a terrible build system.

> What!?

Greetz to asch, tanner, agrant, jblatz, and dthiel. <3
