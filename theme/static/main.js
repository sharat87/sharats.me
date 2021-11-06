window.onload = main

function main() {
	document.body.addEventListener("click", onBodyClick)

	if (document.cookie.match(/(^|;\s*)cookiesOk=1(;|$)/)) {
		cookiesOkSave()  // Save again for it to expire in seven days from now.
	} else {
		document.getElementById("cookiesOkBox").classList.remove("hide")
	}

	for (const el of document.querySelectorAll("sup a.footnote-ref")) {
		// TODO: Move footnote tooltips to build-time.
		el.setAttribute("title", document.getElementById(el.getAttribute("href").slice(1)).textContent.trim())
	}

	for (const el of document.querySelectorAll(".hl")) {
		const buttons = []
		if (el.dataset.lang == "pycon")
			buttons.push(`<button class=console-toggle-btn title="Hide output and '&gt;&gt;&gt;' prompt">&gt;&gt;&gt;</button>`)
		if (el.dataset.lang == "console")
			buttons.push(`<button class=console-toggle-btn title="Hide output and prompt strings">$</button>`)
		if (el.querySelector(".filename")) {
			buttons.push(`<button data-click=downloadCodeBlock class=download-btn>Download</button>`)
		}
		buttons.push("<button data-click=copyCodeBlock class=copy-btn>Copy</button>")
		el.querySelector(".btns").innerHTML = buttons.join("\n")
	}

	document.body.addEventListener("click", (event) => {
		if (event.target.matches("a[href='#']") || event.target.closest("a[href='#']") !== null) {
			event.preventDefault()
		}
	})

	document.body.addEventListener("animationend", event => {
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

function timeSince(date) {
	let i, u, s = Math.round((new Date() - Date.parse(date)) / 100000)
	if (s < 0) return "<span style='color:red'><b>warp zone future</b></span>"
	else if ((i = Math.round(s / 315360)) >= 1) u = "year"
	else if ((i = Math.round(s / 25920)) >= 1) u = "month"
	else if ((i = Math.round(s / 864)) >= 1) u = "day"
	return u ? `~${i} ${u}${i > 1 ? "s" : ""} ago` : "today"
}

function cookiesOkSave() {
	const date = new Date()
	date.setTime(date.getTime() + (7*24*60*60*1000))
	document.cookie = "cookiesOk=1; expires=" + date.toUTCString() + "; path=/"
	document.getElementById("cookiesOkBox").classList.add("hide")
}

function onBodyClick(event) {
	if (event.target.classList.contains("console-toggle-btn"))
		toggleConsoleCeremony(event.target)
	else if (event.target.dataset.click)
		window[event.target.dataset.click](event)
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

function toggleConsoleCeremony(btn) {
	const preEl = btn.closest(".hl").querySelector("pre")
	for (const el of preEl.querySelectorAll("span.gp, span.go"))
		el.classList.toggle("hide")
}

function loadComments(event) {
	event.target.remove()
	document.getElementById("disqus_thread").innerHTML = "Loading comments&hellip;"
	const s = document.createElement("script")
	s.async = true
	s.src = "//" + DISQUS_SITENAME + ".disqus.com/embed.js"
	s.setAttribute("data-timestamp", +new Date())
	document.body.appendChild(s)
}
