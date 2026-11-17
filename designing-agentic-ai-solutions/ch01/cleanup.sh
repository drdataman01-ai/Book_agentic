#!/usr/bin/env bash
# Lab 1 deploys nothing. This script only lists anything in your project that can cost money.
set -euo pipefail
"$(dirname "$0")/../setup/list_resources.sh"
