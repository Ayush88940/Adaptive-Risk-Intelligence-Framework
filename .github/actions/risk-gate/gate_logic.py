import json
import argparse
import requests
import sys

def main():
    parser = argparse.ArgumentParser(description="CI/CD Risk Gate Logic")
    parser.add_argument("--build-id", required=True)
    parser.add_argument("--url", required=True)
    parser.add_argument("--scan-path", required=True)
    args = parser.parse_args()

    try:
        with open(args.scan_path, 'r') as f:
            scan_data = json.load(f)
        
        # In a real scenario, we'd map SonarQube/Trivy outputs to our Vulnerability model
        # For now, we assume the input is already in our expected format or we mock the mapping
        vulnerabilities = scan_data.get("vulnerabilities", [])
        
        # Auto-mapping for Bandit if standard format is detected
        if not vulnerabilities and "results" in scan_data:
            print("Detected Bandit JSON format. Mapping results to ACRIF model...")
            for issue in scan_data["results"]:
                sev_map = {"LOW": 3.0, "MEDIUM": 6.0, "HIGH": 9.0}
                conf_map = {"LOW": 0.4, "MEDIUM": 0.7, "HIGH": 1.0}
                vulnerabilities.append({
                    "id": issue["test_id"],
                    "severity": sev_map.get(issue["issue_severity"], 5.0),
                    "exploitability": conf_map.get(issue["issue_confidence"], 0.5),
                    "exposure": 0.8,
                    "criticality": 0.7,
                    "stage": "prod",
                    "historical": False
                })
        
        payload = {
            "build_id": args.build_id,
            "vulnerabilities": vulnerabilities
        }
        
        response = requests.post(f"{args.url}/calculate-risk", json=payload)
        response.raise_for_status()
        
        result = response.json()
        
        print(f"::notice title=Risk Analysis::Build {args.build_id} - Score: {result['risk_score']} - Decision: {result['decision']}")
        print(f"Recommendation: {result['recommendation']}")
        
        if result['decision'] == "BLOCK":
            print("::error::Deployment BLOCKED due to high risk.")
            sys.exit(1)
        else:
            print("Deployment ALLOWED.")
            
    except Exception as e:
        print(f"::error::Error during risk analysis: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
