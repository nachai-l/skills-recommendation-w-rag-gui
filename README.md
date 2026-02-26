# Skills Recommendation GUI

Streamlit web application for discovering and curating professional skill recommendations powered by a RAG (Retrieval-Augmented Generation) API.

## Features

- Natural language search for skill recommendations
- Detailed skill view with reasoning, evidence, and proficiency criteria
- Select and curate skills of interest
- Export selections to CSV or Excel

## Tech Stack

- **Python 3.12**
- **Streamlit** — interactive UI
- **Pandas** — data handling and export
- **Requests** — API communication
- **Docker** — containerised deployment on Google Cloud Run

## Project Structure

```
├── app.py                      # Streamlit entry point
├── configs/parameters.yaml     # API, defaults, and UI configuration
├── functions/
│   ├── core/
│   │   ├── api_client.py       # HTTP client for the recommendation API
│   │   ├── state.py            # Session state management
│   │   └── export.py           # CSV / XLSX export logic
│   └── utils/
│       ├── config.py           # YAML config loader and dataclasses
│       └── text.py             # Text truncation and formatting helpers
├── tests/                      # Pytest test suite
├── Dockerfile
└── requirements.txt
```

## Quick Start

### Local

```bash
pip install -r requirements.txt
streamlit run app.py
```

### Docker

```bash
docker build -t skills-gui .
docker run -p 8080:8080 skills-gui
```

### Running Tests

```bash
pip install pytest
python -m pytest tests/ -v
```

## Configuration

All settings live in `configs/parameters.yaml`:

| Section    | Key                  | Description                        |
|------------|----------------------|------------------------------------|
| `api`      | `base_url`           | Backend recommendation API URL     |
| `api`      | `endpoint_recommend`  | Recommend endpoint path           |
| `api`      | `endpoint_health`     | Health check endpoint path        |
| `api`      | `timeout_seconds`     | Request timeout                   |
| `defaults` | `top_k`              | Max skills returned               |
| `defaults` | `top_k_vector`       | Vector search limit               |
| `defaults` | `top_k_bm25`        | BM25 search limit                 |
| `defaults` | `debug`              | Enable debug mode                 |
| `ui`       | `page_title`         | Browser tab title                 |
| `ui`       | `preview_chars`      | Skill text truncation length      |
| `ui`       | `max_display_rows`   | Max rows in results table         |
