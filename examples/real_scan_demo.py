import subprocess
import json
import requests
import sys
import os

# API Config
API_URL = "http://localhost:8000/calculate-risk"

def run_real_scan(target_path):
    print(f"--- ACRIF Real-World Scan Demo ---")
    print(f"Target: {target_path}")
    print("Running Bandit SAST Scanner...")

    try:
        # Run Bandit scan
        result = subprocess.run(
            ["bandit", "-r", target_path, "-f", "json"],
            capture_output=True,
            text=True
        )
        
        # Parse JSON output (Bandit returns 1 if issues found, which is fine)
        scan_data = json.loads(result.stdout)
        results = scan_data.get("results", [])
        
        if not results:
            print("No vulnerabilities found by Bandit! Try a different directory or add a mock security issue.")
            return

        print(f"Found {len(results)} potential issues. Mapping to ACRIF Intelligence Layer...")

        # Map Bandit findings to ACRIF format
        vulnerabilities = []
        for issue in results:
            # Map Bandit "issue_severity" to 0-10 scale
            sev_map = {"LOW": 3.0, "MEDIUM": 6.0, "HIGH": 9.0}
            conf_map = {"LOW": 0.4, "MEDIUM": 0.7, "HIGH": 1.0}
            
            vulnerabilities.append({
                "id": issue["test_id"],
                "severity": sev_map.get(issue["issue_severity"], 5.0),
                "exploitability": conf_map.get(issue["issue_confidence"], 0.5),
                "exposure": 0.8, # Assumption: Web exposure
                "criticality": 0.7,
                "stage": "prod",
                "historical": False
            })

        # Send to ACRIF
        payload = {"vulnerabilities": vulnerabilities}
        response = requests.post(API_URL, json=payload)
        decision = response.json()

        print("\n" + "="*50)
        print(f"TOTAL ISSUES ANALYZED: {len(results)}")
        print(f"ACRIF AGGREGATE RISK SCORE: {decision['risk_score']:.2f}/100")
        print(f"FINAL DECISION: {decision['decision']}")
        print(f"RECOMMENDATION: {decision['recommendation']}")
        print("="*50)
        print("\nDashboard updated with live data from the scan!")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "."
    run_real_scan(target)
