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

titlecounter = 0
headers = []
figurecount = 1

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
    pass
  elif isinstance(elem, pf.Header):
    #with open("/tmp/log.txt", "a") as fd:
    #  fd.write(repr(elem) + "\n")
    headers.append(elem)
    elem.identifier = elem.identifier + str(len(headers))
  #elif isinstance(elem, pf.Note):
  #  print("footnote: " + repr(elem))
  #  pass
  elif isinstance(elem, pf.CodeBlock):
    code = elem.text.encode()
    classes = elem.classes

    lang = 'txt' if len(classes) == 0 else classes[0]
    if lang in ['bash', 'sh', 'console']:
      proc = subprocess.run(['highlight', '--list-scripts=langs'], capture_output=True)
      if proc.returncode == 0:
        o = proc.stdout.decode('utf-8')
        for line in o.split("\n"):
          if line.startswith('Bash'):
            lang = line.split(":")[1].strip().split(" ")[0]
            break
      if lang == 'txt':
        if platform.system() == "Darwin":
          lang = 'shellscript'
        else:
          lang = 'sh'

    argv = ['highlight']
    argv += ['-s', 'solarized-dark' if lang == 'txt' or lang == 'console' else 'molokai']
    argv += ['-O' , 'html']
    argv += ['--inline-css']
    argv += ['-S' , lang]
    argv += ['--font' , "'DejaVu Sans Mono', monospace; padding: 1rem; border-radius: 2px; overflow-x: auto"]
    argv += ['-f' , '--enclose-pre']

    #print(argv)
    proc = subprocess.run(argv, input=code, capture_output=True)
    if proc.returncode != 0:
      sys.stderr.write("highlight returned non-zero for {}\n".format(argv))
      sys.stderr.buffer.write(proc.stderr)
      return elem

    output = proc.stdout.decode('utf-8')
    if lang == 'console':
      start_pos = output.find('>')+1
      end_pos = output.find('</pre>')
      content = output[start_pos:end_pos]
      lines = content.split('\n')
      nlines = []
      for line in lines:
        if line.startswith('$$ '):
          nlines.append(line.replace('$$', '#', 1))
        else:
          nlines.append(line)
      ncontent = '\n'.join(nlines)
      output = output[:start_pos] + ncontent + output[end_pos:]
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

def entrypoint(_in=None, _out=None, _headers=None):
  global headers
  headers = []
  if _in is None:
    pf.run_filter(header)
  else:
    if _headers != None:
      _headers.append(headers)
    return pf.run_filter(header, input_stream=_in, output_stream=_out)

if __name__ == "__main__":
  entrypoint()
