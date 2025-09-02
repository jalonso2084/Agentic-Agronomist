# Agentic Agronomist for Potato Late Blight Management

An AI‑powered **virtual agronomist** for potato late blight (*Phytophthora infestans*). The system integrates real‑time weather, epidemiological rules, field history, a small literature library (RAG), and (phase 2) a vision model for leaf images. A central **agentic planner** orchestrates independent tools and produces:

* a **machine‑readable JSON record** (for apps/dashboards), and
* a **short human summary** (EN/ES) with citations when available.

> **Why agentic?** Instead of a rigid pipeline, a planner selects, sequences, and retries tools, with budgets for time and cost.

---

## Table of Contents

* [Features](#features)
* [How It Works](#how-it-works)
* [Toolbox](#toolbox)
* [Architecture](#architecture)
* [Quickstart](#quickstart)

  * [Prerequisites](#prerequisites)
  * [Install](#install)
  * [Configuration](#configuration)
  * [Run a Demo](#run-a-demo)
* [Outputs](#outputs)
* [Metrics & Logging](#metrics--logging)
* [Data Licensing & Attribution](#data-licensing--attribution)
* [Privacy](#privacy)
* [Roadmap](#roadmap)
* [Repository Structure](#repository-structure)
* [Contributing](#contributing)
* [FAQ](#faq)
* [Contact](#contact)

---

## Features

* **Agentic planner** (`agent_planner.py`) orchestrates tools with retries and budgets.
* **Weather → Rules** risk scoring (supports **Hutton** and **Smith Period** variants, locally calibratable).
* **Knowledge** lookup (CSV starter; optional **Neo4j** backend).
* **RAG** over a curated literature folder; returns citations.
* **Vision leaf classifier** (phase 2) via TensorFlow Lite, returns label + confidence + (optional) saliency.
* **Operational hygiene**: explicit I/O contracts, tests, linting, versioning, audit logs.
* **Edge/cloud hybrid** with **offline degraded mode**.

---

## How It Works

1. **Planner** gathers context (field, time, coordinates) and calls the weather fetcher.
2. **Epidemiological rules** classify late‑blight risk (e.g., Low/Medium/High) from recent weather.
3. **Knowledge querier** loads field details (variety, sprays, compliance) to tailor advice.
4. **Literature search (RAG)** fetches short, verifiable snippets for key claims.
5. *(Phase 2)* **Vision classifier** can validate leaf symptoms from a phone/drone photo.
6. Planner synthesizes all evidence into **JSON output** + **human summary** (EN/ES).

---

## Toolbox

| Tool                    | Location                                 | Purpose                                                                   | Notes                                                                         |
| ----------------------- | ---------------------------------------- | ------------------------------------------------------------------------- | ----------------------------------------------------------------------------- |
| Weather Data Fetcher    | `fetch_weather.py`                       | Pull recent hourly weather from Open‑Meteo; **failover**: Visual Crossing | Decoupled provider design; attribution/licensing below                        |
| Epidemiological Rules   | `epirules/`                              | Compare weather to agronomist‑approved rules                              | **Hutton** vs **Smith** criteria (see below)                                  |
| Knowledge Querier       | `knowledge_querier.py`                   | Read field/variety/sprays/compliance                                      | CSV starter; optional **Neo4j** (`neo4j://…`)                                 |
| Literature Search (RAG) | `literature_searcher.py` + `literature/` | Curated docs → citations in answers                                       | Use doc+section; for page cites, store PDFs                                   |
| Vision Leaf Classifier  | `vision_classifier.py` + `model.tflite`  | Analyze leaf images → label + confidence                                  | Export TFLite from Teachable Machine; use `tflite-runtime` for light installs |

> **Hutton vs Smith (used by rules)**
>
> * **Hutton**: Two consecutive days each with **min temp ≥ 10 °C** and **≥ 6 h** at **RH ≥ 90%**.
> * **Smith Period** (legacy): Two consecutive days each with **min temp ≥ 10 °C** and **≥ 11 h** at **RH ≥ 90%**.
>
> Choose the rule set and thresholds in `rules.yaml`, and calibrate locally.

---

## Architecture

```text
User request → Planner
  ├─ Weather fetcher (Open‑Meteo → Visual Crossing failover)
  ├─ Rules checker (Hutton/Smith)
  ├─ Knowledge querier (CSV/Neo4j)
  ├─ Literature search (RAG over curated docs)
  └─ (Phase 2) Vision classifier (TFLite)

Synthesis → { JSON record + EN/ES summary (+ citations) }
Logging → metrics.jsonl, audit logs
```

**Degraded/offline mode**: If cloud LLM or network is unavailable, planner runs **Weather → Rules** locally and returns a brief, lower‑confidence summary (citations may be omitted).

---

## Quickstart

### Prerequisites

* **Python 3.12**
* **Visual Crossing API key** (only used as weather backup)

### Install

Clone the repo and create a virtual environment.

**Windows (PowerShell)**

```powershell
# Clone
git clone https://github.com/jalonso2084/agentic-agronomist.git
cd agentic-agronomist

# Create & activate venv
py -3.12 -m venv .venv
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

**macOS/Linux (bash/zsh)**

```bash
# Clone
git clone https://github.com/jalonso2084/agentic-agronomist.git
cd agentic-agronomist

# Create & activate venv
python3.12 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

**Suggested `requirements.txt`**

```txt
requests
pyyaml
pandas
python-dotenv
tenacity
pydantic
Pillow
# Light TFLite inference on non‑Windows
tflite-runtime; sys_platform != "win32"
# Full TF CPU wheel on Windows (if needed)
tensorflow>=2.18; sys_platform == "win32"
loguru
```

### Configuration

Create a `.env` file in the project root:

```env
VISUAL_CROSSING_API_KEY=YOUR_KEY_HERE
```

Adjust the project data and rules:

* `rules.yaml` — select **hutton** or **smith** and tweak thresholds.
* `farm_data.csv` — define fields (ID, variety, last sprays, organic status, etc.).
* `literature/` — add small, trusted documents (guides, lists, standards). Use `.txt` (doc+section) or PDFs (doc+page).
* *(Optional)* **Neo4j** — set a `neo4j://` URI and credentials in `knowledge_querier.py` to switch from CSV.

### Run a Demo

From your activated environment:

```bash
python agent_planner.py
```

The demo will run the tools and synthesize a recommendation for **`FIELD_002`** using **`test_leaf.jpg`** (if present), printing a human summary and saving a JSON record.

---

## Outputs

### JSON record (example)

```json
{
  "field_id": "FIELD_002",
  "timestamp": "2025-09-02T12:34:56Z",
  "risk": {
    "label": "High",
    "rule_set": "hutton",
    "evidence": {"temp_min_c": 11.2, "hours_rh_ge_90": [7.1, 6.4]}
  },
  "knowledge": {"variety": "Amarilis", "organic": true, "last_spray": "2025-08-24"},
  "rag": [{"doc": "local_guide.txt", "section": "blight_risk_window"}],
  "vision": {"label": "late_blight", "confidence": 0.88},
  "planner": {"latency_ms": 912, "tools_called": ["weather", "rules", "kg", "rag", "vision"]}
}
```

### Human summary (example)

> **EN**: Hutton criteria met on the last two days (≥10 °C and ≥6 h at RH≥90%). Variety *Amarilis* with recent spray on 24‑Aug. Consider a protectant‑to‑systemic rotation per current MoA guidance; see cited local guide sections.
>
> **ES**: Se cumplieron los criterios de Hutton en los últimos dos días (≥10 °C y ≥6 h con HR≥90%). Variedad *Amarilis* con aplicación reciente el 24‑ago. Considere una rotación protectante‑sistémico según la guía vigente de MoA; ver secciones citadas del documento local.

---

## Metrics & Logging

* **`metrics.jsonl`** — one line per run with: `timestamp`, `latency_ms`, `tools_called`, `failures`, optional token/cost proxies.
* **Audit logs** — tool calls and parameters (redacted) for traceability.

Example line:

```json
{"t":"2025-09-02T12:34:56Z","latency_ms":912,"tools":["weather","rules","kg","rag"],"failures":[]}
```

---

## Data Licensing & Attribution

* **Open‑Meteo**: API data are **CC BY 4.0**; the **Free API tier** is for **non‑commercial** use. Some upstream datasets (e.g., UK Met Office) may impose **CC BY‑SA 4.0** on derived products. Attribute accordingly in outputs.
* **Visual Crossing**: Commercial provider; usage and redistribution are governed by your plan/terms. Do not re‑share raw data unless permitted.
* **FRAC/FRAG documents**: Treat as read‑only references; check national labels/registrations before making product‑specific suggestions.

> This repository’s **code** uses a permissive license (MIT/Apache‑2.0). Any **original data** you publish here should declare a separate data license.

---

## Privacy

* No personal data are stored. Field coordinates are processed privately.
* Shared maps use **randomized offsets** (geo‑indistinguishability) rather than fixed jitter.
* Role‑based access can restrict knowledge/field views.
* All tool calls are **audit‑logged**.

---

## Roadmap

* **Phase 1 — Basic loop**: Weather → Rules + CSV knowledge + RAG + planner + offline fallback. Publish EN/ES report template. Target ≥80% agreement with a reference model on risk labels.
* **Phase 2 — Images & explanations**: Add vision model; show confidence; add readable explanation panels and a small dashboard. Target ≥70% agreement with experts on MoA **and** rotation/interval choice; report κ.
* **Phase 3 — Learn & share**: Append‑only write‑backs to knowledge; active learning on uncertain cases; publish anonymized dataset.
* **Phase 4 — Scale**: Add another disease (e.g., early blight) with minimal planner changes; maintain bilingual support.

---

## Repository Structure

```text
agentic-agronomist/
├─ agent_planner.py
├─ fetch_weather.py
├─ epirules/
│  ├─ __init__.py
│  └─ rules_core.py
├─ knowledge_querier.py
├─ literature_searcher.py
├─ vision_classifier.py
├─ rules.yaml
├─ farm_data.csv
├─ literature/
│  └─ *.txt | *.pdf
├─ test_leaf.jpg
├─ model.tflite
├─ requirements.txt
├─ .env.example
└─ README.md
```

---

## Contributing

1. Fork → feature branch → PR (with tests).
2. Keep tool **I/O contracts** explicit (use `pydantic`).
3. Add **10–20 sample tests** per tool with expected JSON outputs.
4. Run linting/tests locally before submitting.

---

## FAQ

**It looks weird after the Windows activation line in Markdown.**
Ensure code blocks are fenced and language‑tagged. This README uses fenced blocks for Windows **PowerShell** and **bash**, which render correctly on GitHub.

**Do I need full TensorFlow?**
If you only run inference with a TFLite model, use **`tflite-runtime`**. Install full `tensorflow` only if you need training or SavedModel features.

**How do I cite pages when my sources are `.txt`?**
Prefer **doc + section/quote** for `.txt`. If you need page numbers, store the original PDF and cite **doc + page**.

**Can I use Neo4j instead of CSV?**
Yes. Provide a `neo4j://` URI and credentials in `knowledge_querier.py`. Keep CSV as the quick‑start backend.

---

## Contact

**Jorge Luis Alonso G.** — [LinkedIn](https://www.linkedin.com/in/jorgeluisalonso/)
