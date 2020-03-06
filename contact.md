---
layout: layouts/page.njk
title: Contact Us
---

<form name=contact netlify>
<table>
<tr>
	<td><label for=email>Your email</label></td>
	<td><input type=email name=email required></td>
</tr>
<tr>
	<td><label for=message>Message</label></td>
	<td><textarea name=message rows=10 cols=30 required></textarea></td>
</tr>
<tr>
	<td colspan=2 style='text-align: center'><button type=submit>Send</button></td>
</tr>
</table>
</form>

<style>
td {
	vertical-align: top;
	border: none;
}

td > input, td > textarea {
	width: 100%;
}
</style>
