---
toc_header_level: 2
---

# Examplely Example

<h2 id="wat">Hello World - not picked up by the ToC due to inline html</h2>

### Not in the ToC due to H3

Hi there.

* some[^aaa]
* bullets[^bbb]
* <a href="#example">#Example</a>[^ccc]
* <a href="#wat" class="title"></a>[^ddd]

[^aaa]: <https://example.com>
[^bbb]: wat
[^ccc]: wat2<br>foo
[^ddd]: wat3

## Code Snippet

```js
let j = await fetch("https://wat.wat", {
  "headers": {
    "x-test": "foo"
  }
}).then((res)=>res.json());
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
![test](./images/test1.jpg){style="width: 1.5in;" figstyle="color: red; width: 35%;" figclass="testing aaa"}
</div>

