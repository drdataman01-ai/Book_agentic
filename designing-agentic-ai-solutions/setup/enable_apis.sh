#!/usr/bin/env bash
# Enable the Google Cloud APIs shared by the labs. Labs enable anything extra in their own setup.sh.
set -euo pipefail
PROJECT="${GOOGLE_CLOUD_PROJECT:-$(gcloud config get-value project 2>/dev/null)}"
[ -n "$PROJECT" ] || { echo "No project set. Run: gcloud config set project <id>"; exit 1; }
echo "Enabling APIs in $PROJECT ..."
gcloud services enable $(grep -v '^#' "$(dirname "$0")/apis.txt" | tr '\n' ' ') --project="$PROJECT"
echo "Done."
