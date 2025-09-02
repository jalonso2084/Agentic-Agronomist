# Agentic Agronomist for Potato Late Blight Management

An AI-powered virtual agronomist designed to support the management of potato late blight.
This agentic system integrates real-time weather data, visual diagnostics from leaf images, and field history.
It orchestrates a set of specialized tools to deliver timely, cited recommendations that help farmers optimize spray schedules and reduce crop loss.

---

## How It Works

This project is not a simple, linear pipeline.
It's an agentic system where a central planner (`agent_planner.py`) intelligently orchestrates a toolbox of specialized, independent Python scripts.
The planner gathers evidence from each tool and synthesizes the findings to produce a context-aware recommendation for a specific agricultural field.

---

## The Agent's Toolbox

The agent uses the following tools to gather evidence:

1. **Weather Data Fetcher**

   * **Script:** `fetch_weather.py`
   * **Purpose:** Pulls recent hourly weather data from reliable sources (Open-Meteo with a failover to Visual Crossing). Provides the raw environmental data needed for risk analysis.

2. **Epidemiological Rules Checker**

   * **Package:** `epirules/`
   * **Purpose:** Compares the fetched weather data against agronomist-approved, locally calibrated rules (e.g., Hutton criteria) to determine if environmental conditions are favorable for a late blight outbreak.

3. **Knowledge Querier**

   * **Script:** `knowledge_querier.py`
   * **Data Source:** `farm_data.csv`
   * **Purpose:** Reads from a simple database to retrieve field-specific details like potato variety, recent spray history, and organic compliance status. This makes the agent's advice *farm-aware*.

4. **Literature Search (RAG)**

   * **Script:** `literature_searcher.py`
   * **Data Source:** `literature/`
   * **Purpose:** Searches a small, curated library of documents (local guides, fungicide lists) to find facts and verifiable citations. This is a Retrieval-Augmented Generation (RAG) tool that grounds the agent's advice in evidence.

5. **Vision-based Leaf Classifier**

   * **Script:** `vision_classifier.py`
   * **Model:** `model.tflite`
   * **Purpose:** Uses a machine learning model (trained via Teachable Machine) to analyze an image of a potato leaf and diagnose its condition (e.g., healthy, late blight, early blight) with a confidence score.

---

## Getting Started

### Prerequisites

* Python 3.12
* An API key for Visual Crossing (for the weather fetcher's backup functionality)

### Setup and Installation

This project uses a Python virtual environment to manage dependencies and avoid version conflicts.

```bash
# Clone the repository
git clone https://github.com/jalonso2084/agentic-agronomist.git
cd agentic-agronomist
```

```bash
# Create the environment using Python 3.12
py -3.12 -m venv .venv
```

```bash
# Activate the environment
.venv\Scripts\activate
```

Your command prompt should now start with `(.venv)`.

```bash
# Install the required libraries
pip install tensorflow pandas pyyaml requests
```

---

## Running the Agent

The main entry point for the system is the `agent_planner.py` script.

1. **Configure the Planner:** Open `agent_planner.py` and add your Visual Crossing API key to the placeholder.
2. **Run the Agent:** Execute the script from your activated `(.venv)` terminal.

```bash
python agent_planner.py
```

The script will run a demonstration, showing how the agent calls each tool in sequence and synthesizes the results into a final recommendation for `FIELD_002` using the `test_leaf.jpg` image.

---

## Configuration

You can easily customize the agent's knowledge and logic by editing the following files:

* `rules.yaml`: Adjust the thresholds for the epidemiological rules.
* `farm_data.csv`: Add or update information about your farm fields.
* `literature/`: Add or edit the `.txt` files to expand the agent's knowledge base.

---

## Contact

Jorge Luis Alonso G.
[LinkedIn](https://www.linkedin.com/in/jorgeluisalonso/)
