{{#configexample3_xml.thing}}

## {{title._text_}}

{{& pre._text_}}

<table>
<thead>
<tr>
<th style="width: 50%">AAA</th>
<th style="width: 50%">BBB</th>
</tr>
</thead>
<tbody>
{{#entries.entry}}
<tr>
<td>
{{& _a}}
</td>
<td>
{{# _b}}{{& .}}{{/ _b}}{{# _text_}}: {{& .}}{{/ _text_}}
</td>
</tr>
{{/entries.entry}}
</tbody>
</table>

{{& post._text_}}

{{/configexample3_xml.thing}}


