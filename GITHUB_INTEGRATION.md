# GitHub Integration Guide: Automated Risk Intelligence 🤖

This guide explains how to set up the **Adaptive Risk Intelligence Framework** to run automatically every time you push code.

## 1. How it works
1. **GitHub Push**: You push code to your repository.
2. **Bandit Scan**: A GitHub Action runs a security scan on your source code.
3. **ACRIF Analysis**: The scan results are sent to your **Risk Engine API**.
4. **The Decision**: 
   - If the Engine says **ALLOW**, the green checkmark appears ✅.
   - If the Engine says **BLOCK** (due to high risk or drift), the build fails ❌.

---

## 2. Setting it up in your repo
Create a file at `.github/workflows/security-gate.yml` and paste the following:

```yaml
name: Adaptive Security Gate
on: [push]

jobs:
  secure-build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run Scan
        run: |
          pip install bandit requests
          bandit -r . -f json -o results.json || true
      
      - name: Risk Gate
        uses: Ayush88940/Adaptive-Risk-Intelligence-Framework/.github/actions/risk-gate@main
        with:
          build_id: ${{ github.run_id }}
          risk_engine_url: 'https://your-api-url.com' # Your hosted FastAPI URL
          scan_results_path: 'results.json'
```

---

## 3. Making the API Public
Since GitHub Actions run on cloud servers, they cannot see your `localhost:8000`. To make it work:

### Option A: Use a Tunnel (For Demos)
1. Install [Ngrok](https://ngrok.com/).
2. Run your backend: `python3 -m engine.main`.
3. Open a tunnel: `ngrok http 8000`.
4. Copy the "Forwarding" URL (e.g., `https://random-id.ngrok-free.app`) and use it as `risk_engine_url` in GitHub.

### Option B: Cloud Hosting (Production)
Deploy your FastAPI backend to a service like **Render**, **Heroku**, or **DigitalOcean**. 

---

## 4. Why this is better than standard tools
Standard tools just give you a list of bugs. **Our Framework** adds "Intelligence":
- **Adaptive**: It remembers previous builds and detects if security is getting worse (**Drift**).
- **Context-Aware**: It grants "Safety Passes" for high-severity bugs if they are in a low-risk environment.

---

**Pro Tip for Evaluators:**
Show them the **Actions tab** in GitHub. When you push a "Dangerous" file (like a hardcoded password), they will see the build turn **Red** and fail because of the **Risk Gate**.
