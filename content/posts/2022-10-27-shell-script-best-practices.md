---
title: Shell Script Best Practices
tags: bash, best-practices, opinion
hn_id: 33354286
---

This article is about a few quick thumb rules I use when writing shell scripts that I've come to appreciate over the years. Very opinionated.

## Things

1. Use `bash`. Using `zsh` or `fish` or any other, will make it hard for others to understand / collaborate. Among all shells, `bash` strikes a good balance between portability and DX.

1. Just make the first line be `#!/usr/bin/env bash`, even if you don't give executable permission to the script file.

1. Use the `.sh` (or `.bash`) extension for your file. It may be fancy to not have an extension for your script, but unless your case explicitly depends on it, you're probably just trying to do clever stuff. Clever stuff are hard to understand.

1. Use `set -o errexit` at the start of your script.
	- So that when a command fails, `bash` exits instead of continuing with the rest of the script.

1. Prefer to use `set -o nounset`. You _may_ have a good excuse to not do this, but, my opinion, it's best to always set it.
	- This will make the script fail, when accessing an unset variable. Saves from horrible unintended consequences, with typos in variable names.
	- When you want to access a variable that may or may not have been set, use `"${VARNAME-}"` instead of `"$VARNAME"`, and you're good.

1. Use `set -o pipefail`. Again, you may have good reasons to not do this, but I'd recommend to always set it.
	- This will ensure that a pipeline command is treated as failed, even if one command in the pipeline fails.

1. Use `set -o xtrace`, with a check on `$TRACE` env variable.
	- For copy-paste: `if [[ "${TRACE-0}" == "1" ]]; then set -o xtrace; fi`.
	- This helps in debugging your scripts, a lot. Like, really lot.
	- People can now _enable_ debug mode, by running your script as `TRACE=1 ./script.sh` instead of `./script.sh`.

1. Use `[[ ]]` for conditions in `if` / `while` statements, instead of `[ ]` or `test`.
	- `[[ ]]` is a bash ~~builtin~~ keyword, and is more powerful than `[ ]` or `test`.

1. Always quote variable accesses with double-quotes.
	- One place where it's _okay_ not to is on the _left-hand-side_ of an `[[ ]]` condition. But even there I'd recommend quoting.
	- When you need the unquoted behaviour, using `bash` arrays will likely serve you much better.

1. Use `local` variables in functions.

1. Accept multiple ways that users can ask for help and respond in kind.
	- Check if the first arg is `-h` or `--help` or `help` or just `h` or even `-help`, and in all these cases, print help text and exit.
	- Please. For the sake of your future-self.

1. When printing error messages, please redirect to stderr.
	- Use `echo 'Something unexpected happened' >&2` for this.

1. Use long options, where possible (like `--silent` instead of `-s`). These serve to document your commands explicitly.
	- Note though, that commands shipped on some systems like macOS don't always have long options.

1. If appropriate, change to the script's directory close to the start of the script.
	- And it's usually always appropriate.
	- Use `cd "$(dirname "$0")"`, which works in _most_ cases.

1. Use `shellcheck`. Heed its warnings.

## Template

```bash
#!/usr/bin/env bash

set -o errexit
set -o nounset
set -o pipefail
if [[ "${TRACE-0}" == "1" ]]; then
	set -o xtrace
fi

if [[ "${1-}" =~ ^-*h(elp)?$ ]]; then
	echo 'Usage: ./script.sh arg-one arg-two

This is an awesome bash script to make your life better.

'
	exit
fi

cd "$(dirname "$0")"

main() {
	echo do awesome stuff
}

main "$@"
```

## Conclusion

I try to follow these rules in my scripts, and they're known to have made at least my own life better. I'm still not consistent though, unfortunately, in following my own rules. So perhaps writing them down this way will help me improve there as well.

Do you have anything you think I should add to this? Please share in the comments!

Edit 1: Included fixes from HN comments at <https://news.ycombinator.com/item?id=33355407> and <https://news.ycombinator.com/item?id=33355077>.

Edit 2: Fix from <https://news.ycombinator.com/item?id=33354759>.
