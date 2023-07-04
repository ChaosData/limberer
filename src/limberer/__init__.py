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
import toml
from collections.abc import Callable
import chevron
import weasyprint
#import markdown # temporary
import subprocess
import io
from bs4 import BeautifulSoup
import re

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

footnotecount = 1
isheader = re.compile('h[1-9]')
headercount = 0

def convert(path, opts, toc, args):
  global headercount
  #print("convert(" + repr(path) + ")")
  proc1 = subprocess.run(['pandoc', '-t', 'json', path], capture_output=True)
  if proc1.returncode != 0:
    sys.stderr.write("error running initial pandoc command: \n")
    sys.stderr.buffer.write(proc1.stderr)
    sys.stderr.write("\n")
    sys.exit(1)
  o1 = proc1.stdout.decode('utf-8')

  if args.debug:
    print(o1)

  # run the panflute filter
  sys.argv = ["html"]
  iw = io.StringIO(o1)
  ow = io.StringIO("")

  headers = []
  _headers = []
  _meta = []
  r = entrypoint(iw, ow, headercount, _headers, _meta)
  opts.update(_meta[0][0])
  ow.seek(0)
  o2 = ow.read()

  if len(_headers) == 1:
    headers = _headers[0]
    headercount += len(headers)

  if "columns" in opts:
    toc.append(opts | {"name": opts['section_name'] + "-columns-title", "issubsection": False})

  #print(repr(headers))
  header_level = int(opts.get('toc_header_level', ['1'])[0])

  for h in headers:
    if h.level <= header_level:
      toc.append(opts | {"name": h.identifier, "issubsection": h.level != 1})

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


def parse_args():
  parser = argparse.ArgumentParser(
    description='A flexible document generator based on WeasyPrint, mustache templates, and Pandoc.'
  )
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
  parser.add_argument('-d', '--debug', action='store_true',
                      help='Debug output.')
  build.add_argument('-E', '--emit-html', metavar='<path>', type=str,
                     default="",
                     help='Emit post-processed HTML to <path>.')

  build.add_argument('config', metavar='<config>', type=str,
                      help="Path to document toml configuration file.")
  args = parser.parse_args()
  return args

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

  config = args.config
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

  config = toml.loads(open(fname, 'r').read())
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
      # markdown
      section_name = section['name']
      section_path = 'sections/{}.md'.format(section['name'])
      content = open_subpath(section_path, 'rb').read()
      #print(repr(content))
      #content = content.decode('utf-8')
      #md = markdown.Markdown(extensions=["meta"])
      #html = md.convert(content)
      #opts = md.Meta | section
      opts = {} | section
      opts['section_name'] = section_name
      html = convert(section_path, opts, toc, args)
      #print("opts: " + repr(opts))
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

      _fns = soup.find(class_="footnotes")
      if _fns is not None:
        _fns = _fns.extract()
        _fns.ol['start'] = str(footnotecount)
        _fns.ol['style'] = f"counter-reset:list-item {footnotecount}; counter-increment:list-item -1;"
        __fns = [c for c in _fns.ol.children if c != "\n"]
        del _fns['id']
        # we already converted all of them above
        #for __fn in __fns:
        #  id = __fn['id']
        #  print("__fn['id']: " + repr(id))
        #  nid = f"{section_name}-{id}"
        #  __fn['id'] = nid
        #  __fnx = soup.find(id=id)
        #  print("__fnx: " + repr(__fnx))
        #  if __fnx is not None:
        #    __fnx['id'] = nid
        for _a in soup.find_all(class_="footnote-ref"):
          # we already converted all of them above
          #_a['id'] = f"{section_name}-{_a['id']}"
          _a['href'] = f"#{section_name}-{_a['href'][1:]}"
          _a.sup.string = str(footnotecount - 1 + int(_a.sup.string))
        for _a in _fns.find_all(class_="footnote-back"):
          _a['href'] = f"#{section_name}-{_a['href'][1:]}"
        _fns.name = 'div'
        footnotecount += len(__fns)

        footnotes = str(_fns)
      html = str(soup)

      opts['html'] = html
      opts['footnotes'] = footnotes
      opts['opts'] = opts # we occasionally need top.down.variable.paths to resolve abiguity
      template = section_template
      if "alt" in section:
        template = open_subpath('templates/{}.html'.format(section['alt']), 'r').read()
      r = chevron.render(template, opts)
      sections.append(r)
    elif section['type'] == 'toc':
      # defer until after we get through everything else
      sections.append(section)
    else:
      # assume in templates/
      template = open_subpath('templates/{}.html'.format(section['type']), 'r').read()
      r = chevron.render(template, config)
      sections.append(r)
      if section['type'] != 'cover' and "title" in section:
        toc.append(opts | {"name": section['type'], "issubsection": False})

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

  if args.debug:
    print(report_html)
  if args.emit_html != "":
    with open(args.emit_html, 'w') as fd:
      fd.write(report_html)
      fd.flush()
      fd.close()

  h = weasyprint.HTML(string=report_html, base_url='./', url_fetcher=fetcher)
  h.write_pdf("./" + '.pdf'.join(fname.rsplit('.toml', 1)))


if __name__ == "__main__":
  main()
