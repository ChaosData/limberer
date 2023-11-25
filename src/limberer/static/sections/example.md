---
toc_header_level: 2
---

# Examplely Example: {{config.title}}

# Examplely Example

<h2 id="wat">Hello World - not picked up by the ToC due to inline html</h2>

### Not in the ToC due to H3

Hi there.

* some[^aaa]
* bullets[^bbb]
* <a href="#example">#Example</a>[^ccc]
* <a class="xrefpg" href="#example">#Example</a>
* <a href="#example-wat" class="title"></a>[^ddd]
* <a class="xref" href="#example2-aaah2">xref to Example2.AAA</a>
* [xref to Example2.AAA](#example2-aaah2){.xref}
* <a class="xrefn" href="#example2-aaah2"></a>
* [](#example2-aaah2){.xrefn}
* <a class="xrefpg" href="#example2-aaah2">xref to Example2.AAA</a>
* [xref to Example2.AAA](#example2-aaah2){.xrefpg}
* <a class="xrefn xrefpg" href="#example2-aaah2"></a>
* [](#example2-aaah2){.xrefn .xrefpg}

1. Hello world
1. Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.
1. Lorem ipsum dolor sit amet, consectetur adipiscing elit,  
   sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.[^eee]

   Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.
1. Hello world

<!-- list break -->

1. Hello world
1. Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.

[^aaa]: <https://example.com>
[^bbb]: wat
[^ccc]: wat2<br>foo
[^ddd]: wat3
[^eee]: wat4

## Code Snippet

```js { lines="true" start="100" highlight="1,5" filename="HelloWorld.js" }
let j = await fetch("https://wat.wat", {
  "headers": {
    "x-test": "foo"
  }
}).then((res)=>res.json());
```
<p><center>Example Snippet of Code</center></p>

<div class="pagebreak"></div>

```js
let j = await fetch("https://wat.wat", {
  "headers": {
    "x-test": "foo"
  }
}).then((res)=>res.json());
```
<figure><figcaption>Example Snippet of Code</figcaption></figure>

```console
$ foo -f bar
$ sudo su
# whoami
root
```

## Table Test

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
    <tr>
      <td>table _body_</td>
      <td>
* table bullet
      </td>
<td>
```
test
```
</td>
      <td>if we place the above `<td>`/`</td>` for the previous cell _with indentation_, pandoc breaks down</td>
    </tr>
    <tr>
      <td>Test</td><td>Hello; world!</td><td></td><td></td>
    </tr>
    <tr>
      <td><ol><li>Table list</li><li>foo</li></ol></td><td></td><td></td><td></td>
    </tr>
    <tr>
      <td><ol><li>Table list</li><li>foo</li></ol></td><td></td><td></td><td></td>
    </tr>
    <tr>
      <td><ol><li>Table list</li><li>foo</li></ol></td><td></td><td></td><td></td>
    </tr>
    <tr>
      <td><ol><li>Table list</li><li>foo</li></ol></td><td></td><td></td><td></td>
    </tr>
  </tbody>
</table>

| First Header  | Second Header |
| ------------- | ------------- |
| Content Cell  | Content Cell  |
| Content Cell  | Content Cell  |

# Image Test

![](./images/test1.jpg){style="width: 30%; margin: auto; display: block;"}

Hello world. Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do
eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim
veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo
consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse
cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non
proident, sunt in culpa qui officia deserunt mollit anim id est laborum.

![test](./images/test1.jpg){style="width: 30%;"}

Test foo bar.

<div class="two-col-fig">
![test](./images/test1.jpg)
<div style="width: 40%">
## Test1

Hello world1. Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do
eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim
veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo
consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse
cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non
proident, sunt in culpa qui officia deserunt mollit anim id est laborum.

## Test1b

Foo bar.
</div>
</div>

<div class="two-col-fig">
<div style="width: 60%">
## Test2

Hello world2. Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do
eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim
veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo
consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse
cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non
proident, sunt in culpa qui officia deserunt mollit anim id est laborum.
</div>
![test](./images/test1.jpg){style="width: 1.5in; border: 1px solid red;" figstyle="color: red; width: 35%;" figclass="testing aaa"}
</div>

