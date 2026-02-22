# 🚀 UTelcom Data Science & MLOps Assignment

## 📖 Overview
This repository contains the complete end-to-end implementation for the UTelcom Data Science assignment. It spans across Agentic Workflows (LLMs), Predictive Modeling (XGBoost), Advanced BigQuery optimization, and MLOps deployment architectures.

---

## 📂 Repository Structure
```text
├── data/               # Contains all synthetic CSV data, including patched `plans.csv` and `customer_subscriptions.csv`.
├── task1/              # Agentic Support Engine (Python scripts, MVP notebooks, external prompt configuration).
├── task2/              # Predictive Churn Modeling (XGBoost & SHAP visualizations).
├── task3/              # BigQuery SQL scripts and optimization strategies.
├── task4/              # MLOps K-S Drift testing script and notebooks.
├── .github/workflows/  # CI/CD Simulation: YAML configurations for automated retraining.
├── Dockerfile          # Multi-stage build for Agentic Application deployment
├── docker-compose.yml  # Containerization and orchestration configurations.
├── run_evaluation.sh   # One-click execution script.
```
---

## 🧠 The Agentic Support Engine (Task 1 - Execution & Evolution)

Task 1 was built iteratively. 
* **Phase 1 (MVP)**: Utilized the `mockllm` background server and a static YAML configuration to satisfy the strict JSON schema.
* **Phase 2 (Dynamic Mock)**: Implemented a pure Python `CustomMockLLM` class in `task1/mvp_solution.ipynb` to calculate discounts dynamically based on dropped calls without needing a live AI model. [Note: These two methods can be run through the ipynb notebook (mvp_solution.ipynb)]
* **Phase 3 (Production)**: Integrated Meta's live `llama3.2` model via local Ollama, utilizing strict prompt engineering (`task1/prompt.txt`) while maintaining unbreakable Python guardrails.

### 🏃 How to Run the Code (Two Methods)

You can run the final Production agent using either a native local setup or a containerized Docker environment.

#### Method 1: Native Local Execution
This method runs the LLM natively on your machine and executes the Python script directly from the root folder.
1. **Set up Python Environment**:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
2. **Start the Local LLM:**
   ```bash
   ollama serve &
   ollama pull llama3.2
   ```
3. **Run the Script:**
   ```bash
   python task1/solution.py
   ```

#### Method 2: One-Click Docker Execution (Recommended)
To ensure a seamless evaluation without manual dependency configurations, this project utilizes Docker Compose. It automatically orchestrates the lightweight Python application alongside an isolated Ollama LLM server.

Simply run the evaluation script from the root directory:
```bash
./run_evaluation.sh
```
(Note: This script builds the application container, spins up the official `ollama` container, pulls the model automatically, and executes the Task 1 Agent).

---

## 🏗️ Architecture & Engineering Notes

### 🐳 Docker Containerization Strategy (Task 4.2)

To satisfy the strict constraint of a "small image size" for Google Artifact Registry, the Docker architecture was deliberately decoupled:

1. Multi-Stage Build: The Dockerfile uses a builder stage to compile heavy Python dependencies (wheels), copying only the compiled binaries and application code into the final python:3.10-slim production image. This reduces the image footprint to <150MB.
2. Decoupled Microservices: Bundling the Ollama server and the 2GB+ Llama 3.2 model weights into the application container was avoided, as it violates separation of concerns. Instead, docker-compose.yml networks the lightweight Agent container to a dedicated LLM container via an HTTP endpoint (LLM_BASE_URL). In a real GCP environment, this mirrors pointing a lightweight Cloud Run app to a heavyweight Vertex AI GPU cluster.

### 🤖 Task 1: Agentic Workflow Architecture

- Approach: Implemented a Custom State Machine rather than heavy frameworks (like LangGraph) to ensure a deterministic, lightning-fast MVP that strictly adheres to sequential business rules.
- Guardrails: An unbreakable Python layer intercepts the LLM output, capping dynamic discounts strictly at $20 prior to Pydantic JSON serialization, guaranteeing business logic safety even if the LLM hallucinates.

### 📈 Task 2: Predictive Modeling (Hybrid Network Churn)

- Approach: NLP transcripts were processed via TF-IDF to maximize execution speed, then merged with Min-Max scaled network logs.
- Class Imbalance: Utilized XGBoost's native scale_pos_weight to aggressively penalize minority class errors, avoiding the noise introduction common with SMOTE.
- Data Leakage Observation: The SHAP waterfall plots revealed a perfect synthetic separation in the generated data (complainers strictly use negative words, non-complainers strictly use neutral words). In a production environment, this 100% accuracy would warrant an immediate audit for target leakage.

### 🗺️ Task 3: Advanced SQL (Fiber Route Optimization)

- Approach: Leveraged a Common Table Expression (CTE) and a Window Function (ROW_NUMBER()) to calculate effective distance penalties and rank routes.
- Scaling Strategy: Documented a comprehensive architectural strategy for 1-billion row tables utilizing Partitioning (by date), Clustering (by hub), and Denormalization (Nested Arrays) to eliminate computationally expensive JOIN operations.

### 🔄 Task 4: MLOps & Drift Pipeline

- Approach: Implemented the two-sample Kolmogorov-Smirnov (K-S) test (task4/drift_check.py) to detect statistical distribution shifts between Staging and Production response lengths.CI/CD. 
- Integration: Authored a GitHub Actions pipeline (retrain.yml) that intercepts non-zero exit codes (sys.exit(1)) from the K-S test to automatically trigger a Champion-Challenger retraining job on Vertex AI when $p < 0.05$.