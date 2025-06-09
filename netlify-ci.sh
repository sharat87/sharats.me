#!/bin/bash

set -xeuo pipefail

curl -LsSf https://astral.sh/uv/install.sh | sh

uv sync --no-dev

export PYTHONPATH=.

exec uv run pelican --ignore-cache --fatal errors
