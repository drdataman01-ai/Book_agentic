#!/usr/bin/env bash
# List resources in the course project that can cost money while they exist.
set -uo pipefail
PROJECT="${GOOGLE_CLOUD_PROJECT:-$(gcloud config get-value project 2>/dev/null)}"
REGION="${GOOGLE_CLOUD_LOCATION:-us-central1}"
echo "Project: $PROJECT   Region: $REGION"
section() { echo; echo "== $1"; }
section "Cloud Run services";   gcloud run services list --project="$PROJECT" --format="value(metadata.name,status.url)" 2>/dev/null
section "Cloud Run jobs";       gcloud run jobs list --project="$PROJECT" --region="$REGION" --format="value(metadata.name)" 2>/dev/null
section "Agent Runtime (reasoning engines)"
curl -s -H "Authorization: Bearer $(gcloud auth print-access-token)" \
  "https://$REGION-aiplatform.googleapis.com/v1/projects/$PROJECT/locations/$REGION/reasoningEngines" \
  | python3 -c "import json,sys; [print(e['name'], e.get('displayName','')) for e in json.load(sys.stdin).get('reasoningEngines',[])]" 2>/dev/null
section "Search data stores"
curl -s -H "Authorization: Bearer $(gcloud auth print-access-token)" -H "X-Goog-User-Project: $PROJECT" \
  "https://discoveryengine.googleapis.com/v1/projects/$PROJECT/locations/global/collections/default_collection/dataStores" \
  | python3 -c "import json,sys; [print(d['name'].split('/')[-1], d.get('displayName','')) for d in json.load(sys.stdin).get('dataStores',[])]" 2>/dev/null
section "Firestore databases";  gcloud firestore databases list --project="$PROJECT" --format="value(name)" 2>/dev/null
section "Cloud SQL instances";  gcloud sql instances list --project="$PROJECT" --format="value(name)" 2>/dev/null
section "Storage buckets";      gcloud storage buckets list --project="$PROJECT" --format="value(name)" 2>/dev/null
section "Pub/Sub topics";       gcloud pubsub topics list --project="$PROJECT" --format="value(name)" 2>/dev/null
echo; echo "Anything listed above that a lab's cleanup.sh should have removed: delete it now."
