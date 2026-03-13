import requests
import json
import sys

# The API URL
API_URL = "http://localhost:8000/calculate-risk"

def run_manual_demo():
    print("--- ACRIF Manual Decision Demo ---")
    print("This script allows you to create a 'Risk Scenario' on the fly to show how the engine decides.")
    
    # 1. Get Context
    stage = input("Enter Deployment Stage (dev/staging/prod) [prod]: ") or "prod"
    criticality = float(input("Enter System Criticality (0.1 to 1.0) [0.8]: ") or "0.8")
    
    # 2. Add a Vulnerability
    print("\nDescribe a vulnerability found in the repo:")
    severity = float(input("  CVSS Severity (0-10) [7.5]: ") or "7.5")
    exploitability = float(input("  Exploit Availability (0.1 to 1.0) [0.5]: ") or "0.5")
    exposure = float(input("  Internet Exposure (0.1 to 1.0) [0.9]: ") or "0.9")
    
    # Construct the payload
    payload = {
        "vulnerabilities": [
            {
                "id": "MANUAL-DEMO-01",
                "severity": severity,
                "exploitability": exploitability,
                "exposure": exposure,
                "criticality": criticality,
                "stage": stage,
                "historical": False
            }
        ]
    }
    
    print("\nSending context to ACRIF Engine...")
    try:
        response = requests.post(API_URL, json=payload)
        result = response.json()
        
        print("\n" + "="*40)
        print(f"ENGINE DECISION: {result['decision']}")
        print(f"RISK SCORE: {result['risk_score']:.2f}/100")
        print(f"RECOMMENDATION: {result['recommendation']}")
        print("="*40)
        print("Check your Live Dashboard now to see this point added!")
        
    except Exception as e:
        print(f"Error: Could not connect to the engine. Is it running? ({e})")

if __name__ == "__main__":
    run_manual_demo()
