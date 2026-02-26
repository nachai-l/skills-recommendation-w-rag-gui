# Skills Recommendation GUI — GCP Cloud Run Deployment (Streamlit)

> Repo: `skills-recommendation-w-rag-gui`
> Target: Cloud Run (managed) in `asia-southeast1`
> Service: `skills-recommendation-gui`
> Artifact Registry: `skills-reco-gui`
> Container: Streamlit (`streamlit run app.py`)
> Backend dependency: calls **skills-recommendation-api** Cloud Run URL

---

## 0) TL;DR

1. Add `Dockerfile` for Streamlit
2. Build + push image to Artifact Registry (Cloud Build)
3. Deploy Cloud Run service (allow unauth)
4. Test UI loads + search works

---

## 1) Prerequisites

### 1.1 Local requirements

* `gcloud` installed and authenticated
* Project access: Cloud Run, Artifact Registry, Cloud Build

### 1.2 Repo requirements

* `app.py` (Streamlit entrypoint)
* `requirements.txt`
* `configs/parameters.yaml` includes API base_url (or set via env at deploy)

---

## 2) Deployment Variables

```bash
PROJECT_ID="poc-piloturl-nonprod"
REGION="asia-southeast1"

AR_REPO="skills-reco-gui"
SERVICE_NAME="skills-recommendation-gui"
IMAGE_NAME="service"
TAG="test-$(date +%Y%m%d-%H%M%S)"

IMAGE_URI="$REGION-docker.pkg.dev/$PROJECT_ID/$AR_REPO/$IMAGE_NAME:$TAG"
SA_NAME="skills-reco-gui-sa"
```

---

## 3) Enable Required Services

```bash
gcloud config set project "$PROJECT_ID"

gcloud services enable \
  run.googleapis.com \
  artifactregistry.googleapis.com \
  cloudbuild.googleapis.com
```

---

## 4) Artifact Registry (Docker) Setup

```bash
gcloud artifacts repositories describe "$AR_REPO" --location="$REGION" >/dev/null 2>&1 || \
gcloud artifacts repositories create "$AR_REPO" \
  --repository-format=docker \
  --location="$REGION" \
  --description="Docker images for Skills Recommendation GUI (Streamlit)"
```

(Optional) Docker auth:

```bash
gcloud auth configure-docker "$REGION-docker.pkg.dev"
```

---

## 5) Service Account + IAM (optional but recommended)

### 5.1 Create service account (if missing)

```bash
gcloud iam service-accounts describe "$SA_NAME@$PROJECT_ID.iam.gserviceaccount.com" >/dev/null 2>&1 || \
gcloud iam service-accounts create "$SA_NAME" \
  --display-name="Skills Recommendation GUI Service Account"
```

### 5.2 Allow logging

```bash
gcloud projects add-iam-policy-binding "$PROJECT_ID" \
  --member="serviceAccount:$SA_NAME@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/logging.logWriter" \
  --condition='expression=true,title=allow-log-writer-skills-reco-gui,description=Allow Cloud Run SA to write logs'
```

> No Secret Manager access needed for GUI (unless you add auth later).

---

## 6) Dockerfile (Streamlit)

Create `Dockerfile` at repo root:

```dockerfile
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8080

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
 && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD streamlit run app.py \
  --server.port=$PORT \
  --server.address=0.0.0.0 \
  --server.headless=true \
  --browser.gatherUsageStats=false
```

---

## 7) `.gcloudignore` (lightweight)

GUI doesn’t need artifacts shipped into container. Keep build uploads small:

```text
.venv/
__pycache__/
*.pyc
.pytest_cache/
.DS_Store
.git/
artifacts/
tests/
```

> `.gcloudignore` matters for Cloud Build upload size.

---

## 8) Build & Push (Cloud Build)

```bash
gcloud builds submit \
  --tag "$IMAGE_URI" \
  --project "$PROJECT_ID"
```

---

## 9) Deploy to Cloud Run

```bash
gcloud run deploy "$SERVICE_NAME" \
  --image "$IMAGE_URI" \
  --region "$REGION" \
  --platform managed \
  --allow-unauthenticated \
  --service-account "$SA_NAME@$PROJECT_ID.iam.gserviceaccount.com" \
  --set-env-vars "LOG_LEVEL=INFO,ENVIRONMENT=prod"
```

Get URL:

```bash
SERVICE_URL="$(gcloud run services describe "$SERVICE_NAME" --region "$REGION" --format='value(status.url)')"
echo "$SERVICE_URL"
```

---

## 10) Test

### 10.1 UI loads

Open `SERVICE_URL` in browser.

### 10.2 End-to-end API call works

In the UI, search `PCR` and confirm results render and export works.

> Optional CLI sanity (GUI itself is a web app, but you can at least confirm it serves HTML):

```bash
curl -I "$SERVICE_URL"
```

---

## 11) Optional production flags

```bash
# avoid cold starts (cost tradeoff)
--min-instances=1

# more headroom
--cpu=1 --memory=1Gi

# allow longer initial loads if needed
--timeout=300
```
