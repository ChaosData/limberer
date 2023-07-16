## {{title}}

{{& pre}}

<table>
<thead>
<tr>
<th style="width: 50%">AAA</th>
<th style="width: 50%">BBB</th>
</tr>
</thead>
<tbody>
{{#entries}}
<tr>
<td>
{{& a}}
</td>
<td>
{{& b}}
</td>
</tr>
{{/entries}}
</tbody>
</table>

{{& post}}
