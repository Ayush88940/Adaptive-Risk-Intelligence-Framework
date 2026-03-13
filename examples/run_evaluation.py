import requests
import json
import time

URL = "http://localhost:8000/calculate-risk"

def run_step(name, file_path):
    print(f"\n--- Running Scenario: {name} ---")
    with open(file_path, "r") as f:
        data = json.load(f)
    
    payload = {
        "build_id": f"build_{int(time.time())}",
        "vulnerabilities": data["vulnerabilities"]
    }
    
    try:
        response = requests.post(URL, json=payload)
        response.raise_for_status()
        res = response.json()
        print(f"Build ID: {res['build_id']}")
        print(f"Risk Score: {res['risk_score']:.2f}")
        print(f"Drift: {res['drift']:.2f}")
        print(f"SDI: {res['sdi']:.2f}")
        print(f"Decision: {res['decision']}")
        print(f"Recommendation: {res['recommendation']}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    print("Starting Experimental Evaluation Simulation...")
    print("Make sure the Risk Engine API is running (python3 -m engine.main)")
    
    run_step("Baseline Build", "examples/mock_scans/baseline.json")
    time.sleep(1) # Ensure unique build IDs
    run_step("High Risk Build", "examples/mock_scans/high_risk.json")
    time.sleep(1)
    run_step("Drift Regression Build", "examples/mock_scans/high_drift.json")
