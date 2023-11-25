#!/usr/bin/env python3

# Copyright (c) 2023 Jeff Dileo.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice,
#     this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

import sys
import argparse
import os
import os.path
import shutil
import rtoml as toml
from collections.abc import Callable
import chevron
import weasyprint
#import markdown # temporary
import subprocess
import io
from bs4 import BeautifulSoup
import re
import time

from .pf import entrypoint

# disable remote url resolution and path traversal
def fetcher(url):
  u = None
  if url.startswith("file://"):
    u = url[7:]
  else:
    u = "./" + url
  cwd = os.path.abspath(".")
  target = os.path.abspath(u)
  if target.startswith(cwd + os.sep):
    return weasyprint.default_url_fetcher("file://" + target)
  else:
    sys.stderr.write("invalid url: " + repr(url) + "\n")
    sys.exit(1)

# disable mustache lambdas. too much magic.
# chevron 0.14.0 only exists on pypi, which is admittedly spooky
# we should dep on 0.13.1 from github or pypi specifically
# but for now we'll mock the 0.14.0 _get_key signature
# which changes wildly between versions
real_get_key = chevron.renderer._get_key
def fake_get_key(key, scopes, warn=None):
  if key.startswith("__") or ".__" in key:
    return ["no soup for you."]
  r = real_get_key(key, scopes, warn=warn)
  if isinstance(r, Callable):
    return ["no soup for you!"]
  return r
chevron.renderer._get_key = fake_get_key
# >>> chevron.render('Hello, {{#mustache}}{{#__class__.__bases__}}{{#__subclasses__}}{{.}}{{/__subclasses__}}{{/__class__.__bases__}}{{/mustache}}!', {'mustache': 'World'})
# 'Hello, no soup for you.!'
# >>> chevron.render('Hello, {{#mustache}}{{#upper}}{{.}}{{/upper}}{{/mustache}}!', {'mustache': 'world'})
# 'Hello, no soup for you!!'

def open_subpath(path, mode='r'):
  cwd = os.path.abspath(".")
  target = os.path.abspath(path)
  if not target.startswith(cwd + os.sep):
    print(f"error: invalid path {repr(path)} references outside of project directory.")
    sys.exit(1)
  return open(path, mode)

def parse_args():
  parser = argparse.ArgumentParser(
    description='A flexible document generator based on WeasyPrint, mustache templates, and Pandoc.'
  )
  parser.add_argument('-d', '--debug', action='store_true',
                      help='Debug output.')
  subparsers = parser.add_subparsers(dest='command', required=True,
                                     title='subcommands',
                                     description='valid subcommands',
                                     help='additional help')

  create = subparsers.add_parser('create')
  create.add_argument('project', metavar='<project>', type=str,
                      help="Name of project to create.")
  create.add_argument('-t', '--template', metavar='<path>', type=str,
                      default="",
                      help='Create from alternative template path instead of the built-in default.')
  build = subparsers.add_parser('build')
  build.add_argument('-P', '--no-pdf', action='store_true',
                      help='Do not emit a PDF.')
  build.add_argument('-E', '--emit-html', metavar='<path>', type=str,
                     default="",
                     help='Emit post-processed HTML to <path>.')
  build.add_argument('configs', metavar='<configs...>', nargs='+', type=str,
                      help="Paths to document toml configuration files.")

  args = parser.parse_args()
  return args

footnotecount = 1
isheader = re.compile('h[1-9]')
headercount = 0
appendix = False
appendix_count = 0

alph = "AABCDEFGHIJKLMNOPQRSTUVWXYZ"
def appendixify(n):
  if n == 0:
    return "A"
  d = []
  while n:
    d.append((n % 26))
    n //= 26
  r = []
  for _d in d[::-1]:
    r.append(alph[_d])
  r[-1] = chr(65+d[0])
  return ''.join(r)

def convert(content, opts, toc, args):
  global headercount
  global appendix_count
  proc1 = subprocess.run(['pandoc', '-t', 'json', '-f', 'markdown'],
                         input=content, text=True, capture_output=True)
  if proc1.returncode != 0:
    sys.stderr.write("error running initial pandoc command: \n")
    sys.stderr.buffer.write(proc1.stderr)
    sys.stderr.write("\n")
    sys.exit(1)
  o1 = proc1.stdout

  #if args.debug:
  #  print(o1)

  # run the panflute filter
  sys.argv = ["html"]
  iw = io.StringIO(o1)
  ow = io.StringIO("")

  headers = []
  _headers = []
  _meta = []
  r = entrypoint(iw, ow, headercount, _headers, _meta, opts['config'])
  opts.update(_meta[0][0])
  ow.seek(0)
  o2 = ow.read()

  if len(_headers) == 1:
    headers = _headers[0]
    headercount += len(headers)

  if "columns" in opts:
    ax = {}
    if appendix:
      ax['appendix_n'] = appendixify(appendix_count)
      appendix_count += 1
    if "title" in opts and opts['title'] != "":
      toc.append(opts | {"name": opts['section_name'] + "-columns-title", "issubsection": False} | ax)
    else:
      opts["title"] = ""
  header_level = int(opts.get('toc_header_level', ['1'])[0])

  ah = False
  for h in headers:
    ax = {}
    if appendix and not ah and h.level == 1:
      ax['appendix_n'] = appendixify(appendix_count)
      ah = True
    if h.level <= header_level:
      toc.append(opts | {"name": opts['section_name'] + "-" + h.identifier, "issubsection": h.level != 1} | ax)

  # pass back to pandoc
  proc2 = subprocess.run(['pandoc', '-f', 'json',
                          '-t', 'html',
                          '--wrap=none'],
                         input=o2, text=True,
                         capture_output=True)
  if proc2.returncode != 0:
    sys.stderr.write("error running initial pandoc command: \n")
    sys.stderr.write(proc2.stderr)
    sys.stderr.write("\n")
    sys.exit(1)
  content = proc2.stdout
  return content

def convert_fancy(content, section_name, opts, toc, args):
  global appendix_count
  global footnotecount

  if args.debug:
    opts['debug_markdown'] = content

  html = convert(content, opts, toc, args)

  if appendix:
    appendix_count += 1
  footnotes = ""
  soup = BeautifulSoup(html, 'html.parser')
  _sns = soup.find_all(lambda e: e.name == 'section' and e.attrs.get('id')!=None)
  for _sn in _sns:
    _snc = [c for c in _sn.children if c != "\n"]
    if len(_snc) > 0:
      if re.match(isheader, _snc[0].name):
        _snc[0]['id'] = _sn['id']
        del _sn['id']
  _iders = soup.find_all(lambda e: e.name != 'article' and e.attrs.get('id')!=None)
  for _ider in _iders:
    _ider['id'] = f"{section_name}-{_ider['id']}"

  #opts["end_footnotes"] = True

  _fns = soup.find(class_="footnotes")
  if _fns is not None:
    _fns = _fns.extract()
    _fns.ol['start'] = str(footnotecount)
    _fns.ol['style'] = f"counter-reset:list-item {footnotecount}; counter-increment:list-item -1;"
    __fns = [c for c in _fns.ol.children if c != "\n"]
    del _fns['id']
    for _a in soup.find_all(class_="footnote-ref"):
      _a['href'] = f"#{section_name}-{_a['href'][1:]}"
      _a.sup.string = str(footnotecount)
      footnotecount += 1
    for _a in _fns.find_all(class_="footnote-back"):
      _a['href'] = f"#{section_name}-{_a['href'][1:]}"
    _fns.name = 'div'
    if "end_footnotes" in opts and (opts["end_footnotes"] == True or opts["end_footnotes"].lower() == "true"):
      footnotes = str(_fns)

  if "end_footnotes" not in opts or (opts["end_footnotes"] != True and opts["end_footnotes"].lower() != "true"):
    for _a in soup.find_all(class_="footnote-ref"):
      _id = _a['href'][1:]
      fn = _fns.find(id=_id)
      tag = soup.new_tag("span", attrs={"class": "footnote"})
      tag['id'] = fn['id']
      for child in list(fn.p.children):
        tag.append(child)
      _a.insert_after(tag)

  html = str(soup)
  opts['html'] = html
  if "end_footnotes" in opts and (opts["end_footnotes"] == True or opts["end_footnotes"].lower() == "true"):
    opts['footnotes'] = footnotes
  opts['opts'] = opts # we occasionally need top.down.variable.paths to resolve abiguity
  return html

def main():
  args = parse_args()

  if args.command == "build":
    build(args)
  elif args.command == "create":
    projpath = args.project
    if os.path.exists(projpath):
      sys.stderr.write(f"error: path '{projpath}' already exists.\n")
      sys.exit(1)
    absprojpath = os.path.abspath(projpath)
    os.makedirs(os.path.dirname(absprojpath), exist_ok=True)

    modpath = os.path.dirname(os.path.abspath(__file__))
    staticpath = os.path.join(modpath, "static")
    templatepath = None
    if args.template == "":
      templatepath = staticpath
    else:
      templatepath = args.template
    shutil.copytree(templatepath, absprojpath)

    dotgitdir = os.path.join(absprojpath, '.git')
    if os.path.exists(dotgitdir):
      shutil.rmtree(dotgitdir)

    projname = os.path.basename(absprojpath)
    if os.path.exists(os.path.join(absprojpath, "project.toml")):
      os.rename(os.path.join(absprojpath, "project.toml"),
                os.path.join(absprojpath, projname + ".toml"))
    else:
      print("project.toml not found in template path " + repr(args.template) + ".... using default.")
      shutil.copyfile(os.path.join(staticpath, "project.toml"),
                os.path.join(absprojpath, projname + ".toml"))

def build(args):
  global footnotecount
  global appendix
  global appendix_count

  config = args.configs[0]
  if not os.path.exists(config):
    sys.stderr.write(f"error: '{config}' not found.\n")
    sys.exit(1)
  if not os.path.isfile(config):
    sys.stderr.write(f"error: '{config}' is not a file.\n")
    sys.exit(1)

  dir, fname = os.path.split(config)
  wd = os.getcwd()
  if dir != "":
    os.chdir(dir)

  config = {
    "highlight": "monokai",
    "highlight_plaintext": "solarized-dark",
    "highlight_font": "'DejaVu Sans Mono', monospace",
    "highlight_style": "border-radius: 2px; overflow-x: auto;",
    "highlight_padding": "padding: 0.5rem 1rem 0.5rem 1rem;",
    "highlight_padding_lines": "padding: 0.25rem 0.5rem 0.25rem 0.5rem;",
    "highlight_line_length": "74",
  }

  config = config | toml.loads(open(fname, 'r').read())
  for path in args.configs[1:]:
    config = config | toml.loads(open(path, 'r').read())

  config['config'] = config # we occasionally need top.down.variable.paths to resolve abiguity

  base_template = open('templates/base.html', 'r').read()
  section_template = open('templates/section.html', 'r').read()
  toc_template = open('templates/toc.html', 'r').read()

  body = ''

  sections = []
  toc = []

  for i in range(len(config['sections'])):
    section = config['sections'][i]
    if section['type'] == 'section':
      if section.get('cont', False) == True:
        continue
      section_name = section['name']
      section_path = 'sections/{}.md'.format(section['name'])

      raw_content = open_subpath(section_path, 'r').read()

      opts = {} | section
      opts['config'] = config
      opts['section_name'] = section_name

      if "conf" in section:
        opts = opts | toml.loads(open_subpath(section['conf'], 'r').read())
      if appendix:
        opts['appendix'] = True
      content = chevron.render(raw_content, opts)

      for j in range(i+1, len(config['sections'])):
        _section = config['sections'][j]
        if _section['type'] != 'section' or _section.get('cont', False) != True:
          break
        _section_name = _section['name']
        _section_path = 'sections/{}.md'.format(_section['name'])
        _raw_content = open_subpath(_section_path, 'r').read()

        _opts = {} | _section
        _opts['config'] = config
        _opts['section_name'] = _section_name

        if "conf" in _section:
          _opts = _opts | toml.loads(open_subpath(_section['conf'], 'r').read())
        _content = chevron.render(_raw_content, _opts)

        content += "\n\n"
        content += _content

      template = section_template
      if "alt" in section:
        template = open_subpath('templates/{}.html'.format(section['alt']), 'r').read()

      html = convert_fancy(content, section_name, opts, toc, args) # sets opts["html"]
      r = chevron.render(template, opts)
      sections.append(r)
    elif section['type'] == 'toc':
      # defer until after we get through everything else
      sections.append(section)
    elif section['type'] == 'appendix_start':
      appendix = True
    elif section['type'] == 'appendix_end':
      appendix = False
    #elif section['type'] == 'appendix_reset':
    #  appendix_count = 0
    else:
      # assume in templates/
      format = section.get('format', "html")
      template = open_subpath(f"templates/{section['type']}.{format}", 'r').read()
      _config = {} | config | section
      if "conf" in section:
        _config = _config | toml.loads(open_subpath(section['conf'], 'r').read())
      if format == 'md':
        section_name = section['name']
        opts = _config
        opts['config'] = _config
        opts['section_name'] = section_name

        if appendix:
          opts['appendix'] = True
        template = chevron.render(template, opts)
        template = convert_fancy(template, section_name, opts, toc, args)

      r = chevron.render(template, _config)
      sections.append(r)
      if section['type'] != 'cover' and "title" in section:
        name = section['type']
        ax = {}
        if appendix:
          ax['appendix_n'] = appendixify(appendix_count)
          appendix_count += 1
        toc.append(opts | {"name": name, "issubsection": False} | ax)

  for section in sections:
    if type(section) == str:
      body += section
      body += "\n"
    else:
      if section['type'] == 'toc':
        r = chevron.render(toc_template, {"sections": toc})
        body += r
        body += "\n"

  config['body'] = body
  report_html = chevron.render(base_template, config)

  if args.emit_html != "":
    with open(args.emit_html, 'w') as fd:
      fd.write(report_html)
      fd.flush()
      fd.close()

  h = None
  if args.debug:
    t0 = time.time()
    h = weasyprint.HTML(string=report_html, base_url='./', url_fetcher=fetcher)
    t1 = time.time()
    print("weasyprint.HTML: {}".format(t1-t0))
  else:
    h = weasyprint.HTML(string=report_html, base_url='./', url_fetcher=fetcher)

  if not args.no_pdf:
    if args.debug:
      t0 = time.time()
      h.write_pdf("./" + '.pdf'.join(fname.rsplit('.toml', 1)))
      t1 = time.time()
      print("write_pdf: {}".format(t1-t0))
    else:
      h.write_pdf("./" + '.pdf'.join(fname.rsplit('.toml', 1)))

if __name__ == "__main__":
  main()
