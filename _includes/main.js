window.onload = main;

function main() {
	setInterval(updateTimes, 60000);
	updateTimes();
	document.body.addEventListener('click', onBodyClick);

	if (document.cookie.match(/(^|;\s*)cookiesOk=1(;|$)/))
		cookiesOkSave();  // Save again for it to expire in seven days from now.
	else
		document.getElementById('cookiesOkBox').classList.remove('hide');

	for (const el of document.querySelectorAll('sup.footnote-ref a'))
		el.setAttribute('title',
			document.getElementById(el.getAttribute('href').slice(1)).firstChild.textContent.trim());

	for (const el of document.querySelectorAll('div.hl')) {
		const buttons = [];
		if (el.dataset.lang == 'pycon')
			buttons.push(`<button type=button class=console-toggle-btn
				title="Hide output and '&gt;&gt;&gt;' prompt">&gt;&gt;&gt;</button>`);
		if (el.dataset.lang == 'console')
			buttons.push(`<button type=button class=console-toggle-btn
				title="Hide output and prompt strings">$</button>`);
		buttons.push('<button type=button class=copy-btn>Copy</button>');
		el.insertAdjacentHTML('beforeEnd', '<div class=btns>' + buttons.join('\n') + '</div>');
	}

	if (!localStorage.noga && !location.hostname.match(/localhost/)) {
		window.dataLayer = window.dataLayer || [];
		function gtag(){dataLayer.push(arguments);}
		gtag('js', new Date());
		gtag('config', 'UA-105705354-1');
		var s = document.createElement('script');
		s.async = true;
		s.src = '//www.googletagmanager.com/gtag/js?id=UA-105705354-1';
		s.setAttribute('data-timestamp', +new Date());
		document.body.appendChild(s);
	}

	document.body.addEventListener('click', (event) => {
		if (event.target.matches('a[href="#"]') || event.target.closest('a[href="#"]') !== null)
			event.preventDefault();
	});

	/*/ Collapse large code blocks.
	let i = 0;
	for (const code of document.querySelectorAll('pre > code')) {
		const newLineMatches = code.innerHTML.match(/\n|<br>/g);
		if (!newLineMatches)
			continue;

		const lineCount = newLineMatches.length;
		if (lineCount < 25)
			continue;

		const previewPat = /^([^\n]*\n){20}/;
		const match = code.innerHTML.match(previewPat);
		if (!match)
			continue;

		code.dataset.fullMarkup = code.innerHTML;
		code.insertAdjacentHTML(
			"beforeBegin",
			`<input type=checkbox class="expand-btn" id="code-${i}"><label for="code-${i}">Show ${lineCount - 20} more lines</label>`
		);
		// const showPartCode = code.innerHTML.substr(0, match[0].length);
		// const openCount = showPartCode.match(/<\w+/g).length,
		// 	closeCount = showPartCode.match(/<\/\w+/g).length;
		// if (openCount !== closeCount)
		code.innerHTML = code.innerHTML.substr(0, match[0].length) +
			`<span class="expanded">` +
			code.innerHTML.substr(match[0].length, code.innerHTML.length) +
			"</span>";

		const table = code.closest('.hltable');
		if (table) {
			const lineNos = table.querySelector('.linenodiv pre');
			lineNos.dataset.fullMarkup = lineNos.innerHTML;
			lineNos.innerHTML = lineNos.innerHTML.substr(0, lineNos.innerHTML.match(previewPat)[0].length);
		}
	} // */

	document.body.addEventListener("change", (event) => {
		if (event.target.matches("input.expand-btn")) {
			const top = event.target.closest(".hltable");
			if (top)
				top.querySelector(".linenodiv .expanded").style = "";
		}
	});
}

function updateTimes() {
	for (const el of document.querySelectorAll("time[data-show-relative]")) {
		if (!el.title)
			el.title = el.textContent;
		el.innerHTML = `${el.title} (${timeSince(el.getAttribute("datetime"))})`;
	}
}

function timeSince(date) {
	let i, u, s = Math.round((new Date() - Date.parse(date)) / 100000);
	if (s < 0) return "<span style='color:red'><b>warp zone future</b></span>";
	else if ((i = Math.round(s / 315360)) >= 1) u = "year";
	else if ((i = Math.round(s / 25920)) >= 1) u = "month";
	else if ((i = Math.round(s / 864)) >= 1) u = "day";
	return u ? `~${i} ${u}${i > 1 ? "s" : ""} ago` : "today";
}

function cookiesOkSave() {
	const date = new Date();
	date.setTime(date.getTime() + (7*24*60*60*1000));
	document.cookie = 'cookiesOk=1; expires=' + date.toUTCString() + "; path=/";
	document.getElementById('cookiesOkBox').classList.add('hide');
}

function onBodyClick(event) {
	if (event.target.classList.contains('copy-btn'))
		copyCodeBlock(event.target);
	else if (event.target.classList.contains('console-toggle-btn'))
		toggleConsoleCeremony(event.target);
	else if (event.target.dataset.click)
		window[event.target.dataset.click](event);
}

function copyCodeBlock(btn) {
	const codeEl = btn.closest('.hl').querySelector('pre code').cloneNode(true);
	for (const el of codeEl.querySelectorAll('.hide, summary'))
		el.remove();
	let text = codeEl.textContent.trim();
	if (text.includes('\n'))
		text += '\n';

	const te = document.createElement('textarea');
	te.style = 'position: fixed; top: 0; left: 0; width: 1px; height: 1px';
	document.body.appendChild(te);
	te.value = text;
	te.select();
	document.execCommand('copy');
	te.remove();

	const prevText = btn.innerText;
	btn.innerText = 'Copied!';
	btn.disabled = 1;
	setTimeout(() => {
		btn.innerText = prevText;
		btn.removeAttribute('disabled');
	}, 1000);
}

function toggleConsoleCeremony(btn) {
	const preEl = btn.closest('.hl').querySelector('pre');
	for (const el of preEl.querySelectorAll('span.gp, span.go'))
		el.classList.toggle('hide');
}

function showFullCodeBlock(event) {
	const code = event.target.previousElementSibling;
	code.innerHTML = code.dataset.fullMarkup;
	event.target.remove();
	const table = code.closest('.hltable');
	if (table) {
		const lineNos = table.querySelector('.linenodiv pre');
		lineNos.innerHTML = lineNos.dataset.fullMarkup;
	}
}

function loadComments(event) {
	event.target.remove();
	document.getElementById('disqus_thread').innerHTML = 'Loading comments&hellip;';
	const s = document.createElement('script');
	s.async = true;
	s.src = '//sharats-me.disqus.com/embed.js';
	s.setAttribute('data-timestamp', +new Date());
	document.body.appendChild(s);
}
