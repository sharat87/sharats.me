---
title: Quick insecure TOTP
tags: hammerspoon, lua, totp, productivity
---

This is about a Hammerspoon script I have that gives me a super-fast way to fill in TOTP fields in MFA logins.

**NOTE**: This method of doing MFA is very likely, very unsafe. If you are any bit unsure about anything here, please stay away from this document.
{.note}

## Hammerspoon

[Hammerspoon](http://www.hammerspoon.org/) is a very convenient and powerful system automation system, that can be programmed in Lua, for macOS. It's been my replacement for AutoHotkey after moving away from Windows.

Install with:

```sh
brew install hammerspoon
```

## TOTP Script

Four pieces to this.

**One**, open `~/.hammerspoon/init.lua`, create if it doesn't exist. Ensure you have the following line, perhaps among many others:

```lua
require("totp-generator").init()
```

**Two**, in `~/.hammerspoon/totp-generator.lua`, put the following content:

```lua
local os = require("os")
local gauth = require("gauth")

local mfa_note_path = os.getenv("HOME") .. "/.hammerspoon/otp-codes.csv"
local keys = nil

function init()
	hs.hotkey.bind({"alt"}, "n", launch)
	hs.pathwatcher.new(mfa_note_path, function()
		keys = loadItems()
	end):start()
	keys = loadItems()
end

local chooser = hs.chooser.new(function(item)
	if item == nil then
		return
	end

	local hash = gauth.GenCode(item._key, math.floor(os.time() / 30))
	hs.eventtap.keyStrokes(("%06d"):format(hash))
end)

chooser:queryChangedCallback(function(query)
	if query == "" then
		chooser:choices(nil)
	end

	local choices = {}

	for _, item in pairs(filter(query, keys) or {}) do
		table.insert(choices, item)
	end

	chooser:choices(choices)
end)

function launch()
	chooser:choices(nil)
	chooser:query("")
	chooser:show()
end

function filter(query, items)
	if query == "" then
		return nil
	end
	local lowerQuery = query:lower()
	local result = {}
	for _, item in pairs(items) do
		if item.text:lower():find(lowerQuery) ~= nil then
			table.insert(result, item)
		end
	end
	return result
end

function loadItems()
	local f = io.open(mfa_note_path, "r")
	local content = f:read("*all")
	f:close()

	local entries = {}
	-- Ref: https://www.lua.org/manual/5.3/manual.html#6.4.1
	for title, key, desc in string.gmatch(content, "%s*(.-)%s*,%s*(.-)%s*,%s*(.-)%s*\n") do
		print(title, desc)
		table.insert(entries, {
			text=title,
			subText=desc,
			_key=string.lower(string.gsub(key, "%s+", "")),
		})
	end

	return entries
end

return {
	init=init,
}
```

**Three**, download the [gauth.lua](https://raw.githubusercontent.com/teunvink/hammerspoon/master/gauth.lua) file, and place it in `~/.hammerspoon` folder. This is what does the bulk of the work, so thanks to [teunvink](https://github.com/teunvink) for this!

**Four**, in the file `~/.hammerspoon/opt-codes.csv`, add your TOTP code data, one per line, like this:

```csv
Mail,abcd efghi jklmn opqrst, Personal Mail Account
Another,onemoretotpcodehere, Another nice account
```

Each line contains three entries, separated by commas. First is a title, short and easily identifiable, second is the TOTP Key, third is a description that you could include any longer explanation for yourself.

The TOTP Key in the second column is given by the MFA provider when configuring MFA. We are usually asked to scan the QR code on our phones when setting this up, but we can also get a TOTP Key, usually hidden behind a button that reads something like `Can't scan the code?`. Copy that key and put an entry here.

Now start/reload Hammerspoon.

Now, while your cursor is in a TOTP field, hit <kbd>Opt+n</kbd> and start searching for any entry from the CSV file, and hit Enter on the entry you want to be filled in.

## Demo

Video: totp-generator-demo.mp4

## Conclusion

Again, this can be very convenient, but is not very secure. The way I use it on my system is quite a bit different from what I demonstrate here, but that's only because I don't want to show off the exact format I am using. So feel free to tweak the CSV format and use something else like JSON or some other encrypted source altogether, like the `pass` CLI, perhaps. But, I can't speak for that.

Keep your keys safe. They are nothing less than passwords.

Thank you for reading.
