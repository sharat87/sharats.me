window.onload = () => {
	for (const el of document.querySelectorAll("sup a.footnote-ref")) {
		// TODO: Move footnote tooltips to build-time.
		el.setAttribute("title", document.getElementById(el.getAttribute("href").slice(1)).textContent.trim())
	}

	for (const el of document.querySelectorAll(".hl")) {
		const buttons = []
		if (el.dataset.lang == "pycon")
			buttons.push(`<button class=console-toggle-btn onclick="toggleConsoleCeremony(event)" title="Hide output and '&gt;&gt;&gt;' prompt">&gt;&gt;&gt;</button>`)
		if (el.dataset.lang == "console")
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

	window.goatcounter = {no_onload: localStorage.getItem("noAnalytics") === "1"}
	const s = document.createElement("script")
	s.dataset.goatcounter = "https://ssk.goatcounter.com/count"
	s.async = "async"
	s.src = "//gc.zgo.at/count.js"
	document.head.appendChild(s)
}

function copyCodeBlock(event) {
	const btn = event.target
	let text = btn.closest(".hl").querySelector("pre.content").textContent.trim()
	if (text.includes("\n"))
		text += "\n"

	const te = document.createElement("textarea")
	te.style = "position: fixed; top: 0; left: 0; width: 1px; height: 1px"
	document.body.appendChild(te)
	te.value = text
	te.select()
	document.execCommand("copy")
	te.remove()

	showGhost(btn, "Copied!")
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
