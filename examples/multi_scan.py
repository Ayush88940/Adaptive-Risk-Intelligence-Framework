import requests
import time
import json

# List of 10 popular Python repos for a pilot study
# The user can expand this to 50+ as needed for the final paper.
REPOS = [
    "https://github.com/psf/requests",
    "https://github.com/pallets/flask",
    "https://github.com/django/django",
    "https://github.com/ansible/ansible",
    "https://github.com/pypa/pip",
    "https://github.com/scikit-learn/scikit-learn",
    "https://github.com/tiangolo/fastapi",
    "https://github.com/python-poetry/poetry",
    "https://github.com/scrapy/scrapy",
    "https://github.com/boto/boto3"
]

API_URL = "http://localhost:8000/scan-repo"

def run_multi_scan():
    print(f"🚀 Starting academic validation scan on {len(REPOS)} repositories...")
    results = []
    
    for repo in REPOS:
        print(f"📦 Scanning {repo}...")
        try:
            response = requests.post(API_URL, json={"repo_url": repo}, timeout=300)
            if response.status_code == 200:
                data = response.json()
                print(f"  ✅ Done. Risk: {data['risk_score']}, Baseline: {data['baseline_score']}")
                results.append(data)
            else:
                print(f"  ❌ Failed: {response.text}")
        except Exception as e:
            print(f"  ❌ Error: {str(e)}")
        
        # Brief pause to avoid rate limiting or heavy load
        time.sleep(2)

    print("\n🏁 Pilot Scan Completed!")
    print(f"Total processed: {len(results)}")

if __name__ == "__main__":
    # Ensure the backend is running before starting this script.
    run_multi_scan()
