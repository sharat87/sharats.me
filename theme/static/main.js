window.onload = () => {
	for (const el of document.querySelectorAll("sup a.footnote-ref")) {
		// TODO: Move footnote tooltips to build-time.
		el.setAttribute("title", document.getElementById(el.getAttribute("href").slice(1)).textContent.trim())
	}

	for (const el of document.querySelectorAll(".hl")) {
		const buttons = []
		if (el.dataset.lang === "pycon")
			buttons.push(`<button class=console-toggle-btn onclick="toggleConsoleCeremony(event)" title="Hide output and '&gt;&gt;&gt;' prompt">&gt;&gt;&gt;</button>`)
		if (el.dataset.lang === "console")
			buttons.push(`<button class=console-toggle-btn onclick="toggleConsoleCeremony(event)" title="Hide output and prompt strings">$</button>`)
		if (el.querySelector(".filename")) {
			buttons.push(`<button onclick="downloadCodeBlock(event)" class=download-btn>Download</button>`)
		}
		buttons.push(`<button onclick="copyCodeBlock(event)" class=copy-btn>Copy</button>`)
		el.querySelector(".btns").innerHTML = buttons.join("\n")
	}

	document.body.addEventListener("click", (event) => {
		if (event.target.matches("a[href='#']") || event.target.closest("a[href='#']") !== null) {
			event.preventDefault()
		}
	})

	document.body.addEventListener("animationend", (event) => {
		if (event.target.className === "ghost") {
			event.target.remove()
		}
	})

	if (location.protocol === "https:" && location.hostname !== "localhost" && localStorage.u !== "1") {
		document.body.insertAdjacentHTML(
			"beforeend",
			`<script async data-website-id="bd2b9a7e-1356-4ead-bb87-596387ad24d4" defer src="//u.sharats.me/main.js"></script>`,
		)
	}
}

function copyCodeBlock(event) {
	const btn = event.target
	let text = btn.closest(".hl").querySelector("pre.content").textContent.trim()
	if (text.includes("\n")) {
		text += "\n"
	}

	navigator.clipboard.writeText(text)
		.then(() => showGhost(btn, "Copied"))
		.catch(err => showGhost(btn, err))
}

function downloadCodeBlock(event) {
	const btn = event.target
	let text = btn.closest(".hl").querySelector("pre.content").textContent.trim()
	if (text.includes("\n"))
		text += "\n"

	const filename = btn.closest(".hl").querySelector(".filename").textContent.trim()

	const el = document.createElement("a")
	el.style.display = "none"
	el.setAttribute("download", filename)
	el.setAttribute("href", "data:text/plain;charset=utf-8," + encodeURIComponent(text))
	document.body.append(el)
	el.click()
	el.remove()

	showGhost(btn, "Downloaded")
}

function showGhost(el, label) {
	const rect = el.getBoundingClientRect()
	document.body.insertAdjacentHTML(
		"beforeend",
		`<div class=ghost style="left: ${rect.x}px; top: ${rect.y}px; min-width: ${rect.width}px; ${rect.height}px">${label}<div>`
	)
}

function toggleConsoleCeremony(event) {
	const btn = event.target
	const preEl = btn.closest(".hl").querySelector("pre")
	for (const el of preEl.querySelectorAll("span.gp, span.go"))
		el.classList.toggle("hide")
}

function loadComments(event) {
	event.target.outerHTML = "Loading comments&hellip;"
	document.body.insertAdjacentHTML("beforeend", `<script async src="//${DISQUS_SITENAME}.disqus.com/embed.js" data-timestamp="${+new Date}"></script>`)
}
