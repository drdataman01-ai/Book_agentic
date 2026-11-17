"""Check that your machine and course project are ready for the labs."""
import os
import shutil
import subprocess
import sys
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / "course.env")
failures = 0


def check(name, ok, hint=""):
    global failures
    print(f"{'OK  ' if ok else 'FAIL'}  {name}" + ("" if ok else f"   -> {hint}"))
    failures += 0 if ok else 1


def run(cmd):
    try:
        return subprocess.run(cmd, capture_output=True, text=True, timeout=60).stdout.strip()
    except Exception:
        return ""


check("Python 3.11 or later", sys.version_info >= (3, 11), "Install Python 3.11+")
check("gcloud installed", shutil.which("gcloud") is not None, "Install the Google Cloud CLI")
check("node installed (for MCP Inspector)", shutil.which("node") is not None, "Install Node.js 20+")
check("course.env exists", (Path(__file__).parent / "course.env").exists(),
      "cp setup/course.env.example setup/course.env")

vertex = os.getenv("GOOGLE_GENAI_USE_VERTEXAI", "True").lower() == "true"
project = os.getenv("GOOGLE_CLOUD_PROJECT", "")
if vertex:
    check("GOOGLE_CLOUD_PROJECT set", bool(project) and project != "agentic-course-12345",
          "Put your project ID in setup/course.env")
    try:
        import google.auth
        creds, _ = google.auth.default()
        check("Application default credentials", creds is not None, "")
    except Exception:
        check("Application default credentials", False, "gcloud auth application-default login")
    billing = run(["gcloud", "billing", "projects", "describe", project,
                   "--format=value(billingEnabled)"])
    check("Billing linked to project", billing.lower() == "true",
          "gcloud billing projects link <project> --billing-account=<id>")
    enabled = run(["gcloud", "services", "list", "--enabled", f"--project={project}",
                   "--format=value(config.name)"])
    check("Vertex AI API enabled", "aiplatform.googleapis.com" in enabled, "./setup/enable_apis.sh")
else:
    check("GOOGLE_API_KEY set (local route)", bool(os.getenv("GOOGLE_API_KEY")),
          "Add GOOGLE_API_KEY to setup/course.env")

try:
    from google import genai
    client = (genai.Client(vertexai=True, project=project,
                           location=os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1"))
              if vertex else genai.Client())
    reply = client.models.generate_content(
        model=os.getenv("MODEL_NAME", "gemini-3.6-flash"),
        contents="In one sentence, say hello to a student starting a course on agent design.")
    check("Gemini call", bool(reply.text), "")
    print("\n" + reply.text.strip())
except Exception as e:  # noqa: BLE001
    check("Gemini call", False, f"{type(e).__name__}: {str(e)[:200]}")

sys.exit(1 if failures else 0)
