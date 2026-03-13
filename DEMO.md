# Live Demo Guide: How to show the ACRIF Working 🚀

When the evaluators ask: **"How do we know this works on a real project?"**, follow these three levels of demonstration.

### Level 1: The "Decision Logic" Demo (Interactive)
The evaluators might say: *"What if I have a high-severity bug but it's only in my internal Dev environment?"*
**Show them this:**
1.  Open a terminal and run: `python3 examples/manual_test.py`
2.  Input **"dev"** as the stage.
3.  Input **"9.0"** as the severity.
4.  **Result:** The engine will likely **ALLOW** it because it's only in Dev.
5.  **Repeat:** Run it again but change stage to **"prod"**. The engine will **BLOCK** it.
*This proves the engine is "Context-Aware".*

---

### Level 2: The "Software Intelligence" Demo (Dashboard)
Show the evaluators the **Live Dashboard** (`http://localhost:5173`).
- **The Points to Explain:**
    - **Risk Drift:** Explain that we don't just look at one build; we look at the "Health Trend". If the bar is green/negative, the developers are making the app safer. If it's red/positive, they are introducing risk.
    - **Security Debt:** Point to the SDI metric. Explain that this is the "Credit Score" for software security. It tracks if the team is fixing bugs or just letting them pile up.

---

### Level 4: The "Live Repository Scan" (Pro Level)
If they give you a real Python folder and say: *"Scan this"*:
1. Run this command:
   ```bash
   python3 examples/real_scan_demo.py [path_to_folder]
   ```
2. **What happens:** It runs a real security tool (**Bandit**) on their code, finds real vulnerabilities (like hardcoded keys or unsafe imports), and pipes them into our **ACRIF Engine** to get a final risk score.

---

### Summary Checklist for a 10/10 Score:
- [ ] **Step 1:** Start Backend Engine (`python3 -m engine.main`).
- [ ] **Step 2:** Start Dashboard (`npm run dev`).
- [ ] **Step 3:** Run `python3 examples/run_evaluation.py` to show the 3 scenarios we analyzed.
- [ ] **Step 4:** Use `python3 examples/manual_test.py` to answer "What if?" questions from evaluators.
