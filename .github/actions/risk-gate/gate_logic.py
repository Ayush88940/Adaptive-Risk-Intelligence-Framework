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
