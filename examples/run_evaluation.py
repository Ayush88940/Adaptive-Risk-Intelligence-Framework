import requests
import json
import time

URL = "http://localhost:8000/calculate-risk"

def run_step(name, file_path, custom_id):
    print(f"\n--- Running Scenario: {name} ---")
    with open(file_path, "r") as f:
        data = json.load(f)
    
    payload = {
        "build_id": custom_id,
        "vulnerabilities": data["vulnerabilities"]
    }
    
    try:
        response = requests.post(URL, json=payload)
        response.raise_for_status()
        res = response.json()
        print(f"Identifier: {res['build_id']}")
        print(f"Risk Score: {res['risk_score']:.2f}")
        print(f"Drift: {res['drift']:.2f}")
        print(f"SDI: {res['sdi']:.2f}")
        print(f"Decision: {res['decision']}")
        print(f"Recommendation: {res['recommendation']}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    print("Starting Experimental Evaluation Simulation...")
    print("Make sure the Risk Engine API is running (python3 -m engine.main)\n")
    
    # 1. Baseline Build
    run_step("Baseline Build", "examples/mock_scans/baseline.json", "stable-release-v1.1.0")
    time.sleep(3) # staggered animation sleep
    
    # 2. Perfect Build (Zero Risk)
    run_step("Perfect Security Build", "examples/mock_scans/perfect_build.json", "production-patch-safeguard")
    time.sleep(3)
    
    # 3. High Risk Build (Simulate regression)
    run_step("High Risk Feature Branch", "examples/mock_scans/high_risk.json", "experimental-feature-untrusted")
    time.sleep(3)
    
    # 4. Low Risk Warning (Simulate minor drift)
    run_step("Minor Dev Warning", "examples/mock_scans/low_risk_warning.json", "dev-staging-patch-v0.9")
    time.sleep(3)
    
    # 5. Massive Drift Regression
    run_step("Critical Drift Regression", "examples/mock_scans/high_drift.json", "emergency-rollback-incident")
