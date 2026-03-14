# Cloud Deployment Guide: Render.com ☁️

Follow these steps to deploy your **Risk-Aware CI/CD Pipeline with Security Scoring** to the cloud so that everyone can access the dashboard and the GitHub action works globally.

## Step 1: Push your code to GitHub
Make sure all your latest changes (including the `render.yaml` and `requirements.txt` I just updated) are pushed to your GitHub repository:
- `git add .`
- `git commit -m "Prepare for cloud deployment"`
- `git push origin main`

## Step 2: Deploy to Render.com
1. Go to [Render.com](https://dashboard.render.com/) and create a free account.
2. Click **"+ New"** -> **"Blueprint"**.
3. Connect your GitHub repository.
4. Render will automatically find the `render.yaml` file and set up:
   - **acrif-backend**: Your API (built using FastAPI).
   - **acrif-dashboard**: Your React UI (built using Vite).
5. Click **"Apply"**.

## Step 3: Wait for Build
- Wait for both services to show a green **"Live"** status.
- Render will give you two URLs:
  - **Backend:** e.g., `https://acrif-backend.onrender.com`
  - **Dashboard:** e.g., `https://acrif-dashboard.onrender.com`

## Step 4: Update your GitHub Action
Now that you have a public API URL, update your `.github/workflows/security-gate.yml`:
1. Change `risk_engine_url` from `localhost` to your new **Backend URL** from Render.

---

### Why this is great for your project:
- **Global Access:** Your evaluators can open your Dashboard from their own computers.
- **Production Grade:** Using `uvicorn` in the cloud shows you can handle real traffic.
- **Automated CI/CD:** Your security gate is now a "cloud-native" feature that truly protects your repo on every push.

**Good luck with the deployment!** 🚀
