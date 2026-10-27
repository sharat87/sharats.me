#!/bin/bash

set -xeuo pipefail

curl -LsSf https://astral.sh/uv/install.sh | sh
# The installer only adds this to PATH in shell profiles, not the running shell.
export PATH="$HOME/.local/bin:$PATH"

exec uv run --no-dev python build.py
