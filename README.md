# Risk-Aware CI/CD Pipeline with Security Scoring

This project builds a smart CI/CD pipeline that evaluates security risks and scores them intelligently using contextual data, and automatically decides whether deployment is safe.

## Project Structure

- `engine/`: Python/FastAPI backend that calculates risk scores, drift, and security debt.
- `dashboard/`: React + Vite frontend for visualizing risk trends and deployment history.
- `.github/actions/risk-gate/`: Custom GitHub Action for CI/CD integration.
- `examples/`: Mock scan results and evaluation scripts.

## Setup and Testing Instructions

### 1. Start the Risk Engine API (Backend)
Open a terminal and run:
```bash
pip install -r requirements.txt
python3 -m engine.main
```
*The API will run at http://localhost:8000*

### 2. Start the Visualization Dashboard (Frontend)
Open a **second** terminal and run:
```bash
cd dashboard
npm run dev
```
*The dashboard will usually run at http://localhost:5173 (check terminal output)*

### 3. Run the Experimental Evaluation (Test Scenarios)
Open a **third** terminal and run:
```bash
python3 examples/run_evaluation.py
```
This script sends 3 mock scenarios (Baseline, High Risk, High Drift) to the engine. You will see the results appearing in both the terminal and the live dashboard!

## Key Metrics
- **Risk Score (R)**: Weighted calculation of severity, exploitability, exposure, and context.
- **Risk Drift**: Change in risk relative to the previous build.
- **Security Debt Index (SDI)**: Cumulative weighted vulnerabilities over time.
