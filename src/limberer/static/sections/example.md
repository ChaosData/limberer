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

