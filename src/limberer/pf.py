#!/usr/bin/env python3

# Copyright (c) 2020-2022 NCC Group,
#               2023 Jeff Dileo.
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

import panflute as pf
import sys
import subprocess
import os
import platform
import base64
from PIL import Image

from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_by_name
from pygments.styles import get_style_by_name

titlecounter = 0
headers = []
metadata = []
figurecount = 1
args = None

lexers = {}
formatters = {}

def stringify(content):
  out = []
  for part in content:
    if isinstance(part, pf.Str):
      out.append(str(part)[4:-1])
    elif isinstance(part, pf.Space):
      out.append(' ')
  return ''.join(out)

def header(elem, doc):
  global titlecounter
  global checkboxcounter
  global figurecount

  if isinstance(elem, pf.Doc):
    m = {k: elem.get_metadata(k) for k in elem.metadata.content}
    metadata.append(m)
  elif isinstance(elem, pf.Header):
    #with open("/tmp/log.txt", "a") as fd:
    #  fd.write(repr(elem) + "\n")
    headers.append(elem)
    #elem.identifier = elem.identifier + str(len(headers) + headercount + 1)
    if elem.identifier == None or elem.identifier == "":
      elem.identifier = str(len(headers) + headercount + 1)
  #elif isinstance(elem, pf.Note):
  #  print("footnote: " + repr(elem))
  #  pass
  elif isinstance(elem, pf.CodeBlock):
    code = elem.text.encode()
    classes = elem.classes
    attrs = elem.attributes
    lang = 'text' if len(classes) == 0 else classes[0]
    style = ""
    if lang in ["text", "console"]:
      style = get_style_by_name(config['highlight_plaintext'])
    else:
      style = get_style_by_name(config['highlight'])
    opts = {
      "style": style,
      "noclasses": True,
    }
    if "lines" in attrs:
      opts["linenos"] = True if attrs["lines"] == "true" else False
      opts["cssstyles"] =  f"color: white; font-family: {config['highlight_font']}; {config['highlight_style']}; {config['highlight_padding_lines']};"
    else:
      opts["cssstyles"] =  f"color: white; font-family: {config['highlight_font']}; {config['highlight_style']}; {config['highlight_padding']};"

    if "start" in attrs:
      opts["linenostart"] = int(attrs["start"])
    if "highlight" in attrs:
      opts["hl_lines"] = [int(l) for l in attrs["highlight"].split(",")]
    if "filename" in attrs:
      opts["filename"] = attrs["filename"]

    lexer = get_lexer_by_name(lang, stripall=True)
    formatter = HtmlFormatter(**opts)
    output = highlight(code, lexer, formatter)

    return pf.RawBlock(output, format='html')
  elif isinstance(elem, pf.Figure):
    imgattrs = elem.content[0].content[0].attributes
    if "figstyle" in imgattrs:
      elem.attributes["style"] = imgattrs["figstyle"]
      del imgattrs["figstyle"]
    if "figclass" in imgattrs:
      elem.attributes["class"] = imgattrs["figclass"]
      del imgattrs["figclass"]
    #print(elem.caption)
    #print(repr(elem.caption.content[0]))
    #print(repr(elem.caption.content[0].content[0].text))
    #elem.caption.content[0].content[0].text = f"Figure {figurecount}: {elem.caption.content[0].content[0].text}"
    pass
  elif isinstance(elem, pf.Image):
    #print(repr(elem))
    #print(elem.title)
    #print(elem.content)
    #if len(elem.content) > 0:
    #  elem.content[0].text = f"Figure {figurecount}: {elem.content[0].text}"
    #  figurecount += 1
    #  print(elem.content[0])
    return elem
    if elem.url.startswith("file://") or elem.url.startswith("./"):
      url = None
      if elem.url.startswith("file://"):
        url = elem.url[7:]
      else:
        url = elem.url[2:]
      f = None
      opts = {}
      if "?" in url:
        f = url.split("?")[0]
        for arg in url.split("?")[1].split("&"):
          k, v = arg.split("=")
          opts[k] = v
      else:
        f = url
      if os.path.realpath(f) == os.path.join(os.path.realpath('.'), f):
        size = ""
        img = Image.open(f)
        width = img.width
        height = img.height
        css_width = "100%"
        scale = int(100*(height / width))+1
        css_padding_top = str(scale) + "%"

        if 'scale' in opts:
          css_width = opts['scale'] + "%"

        html = "<div style=\"margin: auto; width:" + css_width + "; background: url('" + url + "') no-repeat; background-size: contain;\"><div style=\"height: 0px; padding-top:" + css_padding_top + ";\">&nbsp;</div></div>"
        return pf.RawInline(html, format='html')
      else:
        sys.stderr.write("image path bad: " + f + "\n")
        sys.stderr.write(os.path.realpath(f) + "\n")
        sys.stderr.write(os.path.join(os.path.realpath('.'), f) + "\n")
  return elem

def entrypoint(_in=None, _out=None, _headercount=0, _headers=None, _meta=None, _config=None):
  global headers
  global metadata
  global headercount
  global config
  headers = []
  if _in is None:
    pf.run_filter(header)
  else:
    if _headers != None:
      _headers.append(headers)
    if _meta != None:
      metadata = []
      _meta.append(metadata)
    if _config != None:
      config = _config
    headercount = _headercount
    return pf.run_filter(header, input_stream=_in, output_stream=_out)

if __name__ == "__main__":
  entrypoint()
