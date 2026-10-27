#!/bin/bash

set -xeuo pipefail

curl -LsSf https://astral.sh/uv/install.sh | sh

uv sync --no-dev

exec uv run python build.py
