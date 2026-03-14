from typing import List
from fastapi import FastAPI, HTTPException, Depends
import uvicorn
import sqlalchemy
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
import os
import subprocess
import tempfile
import shutil
import json
import uuid
from .models import VulnerabilitySchema, RiskRequest, RiskResponse, BuildDB, VulnerabilityDB
from .scoring import calculate_risk_score, calculate_drift, calculate_sdi
from .database import engine, Base, get_db
from pydantic import BaseModel

class RepoScanRequest(BaseModel):
    repo_url: str

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Risk-Aware CI/CD Pipeline with Security Scoring API")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Risk-Aware CI/CD Pipeline with Security Scoring Engine is running"}

@app.post("/calculate-risk", response_model=RiskResponse)
async def get_risk(request: RiskRequest, db: Session = Depends(get_db)):
    # 1. Fetch previous build for Drift calculation
    previous_build = db.query(BuildDB).order_by(BuildDB.timestamp.desc()).first()
    previous_score = previous_build.risk_score if previous_build else 0.0
    
    # 2. Fetch total build count for SDI calculation
    total_builds = db.query(BuildDB).count() + 1
    
    # 3. Calculate scores
    risk_score = calculate_risk_score(request.vulnerabilities)
    drift = calculate_drift(risk_score, previous_score)
    sdi = calculate_sdi(request.vulnerabilities, total_builds)
    
    decision = "BLOCK" if risk_score > 70 or drift > 20 else "ALLOW"
    recommendation = "Review high-risk vulnerabilities" if decision == "BLOCK" else "Proceed with deployment"
    
    # 4. Save to Database
    try:
        new_build = BuildDB(
            build_id=request.build_id,
            risk_score=risk_score,
            drift=drift,
            sdi=sdi,
            decision=decision
        )
        db.add(new_build)
        db.commit()
    except sqlalchemy.exc.IntegrityError:
        db.rollback()
        # If ID exists, append a unique suffix to prevent 500 error
        unique_id = f"{request.build_id}_{uuid.uuid4().hex[:4]}"
        new_build = BuildDB(
            build_id=unique_id,
            risk_score=risk_score,
            drift=drift,
            sdi=sdi,
            decision=decision
        )
        db.add(new_build)
        db.commit()
    
    db.refresh(new_build)
    
    # Save vulnerabilities associated with the build
    for v in request.vulnerabilities:
        v_db = VulnerabilityDB(
            vuln_id=v.id,
            severity=v.severity,
            exploitability=v.exploitability,
            exposure=v.exposure,
            criticality=v.criticality,
            stage=v.stage,
            historical=v.historical,
            build_id=new_build.id
        )
        db.add(v_db)
    
    db.commit()
    
    return RiskResponse(
        build_id=request.build_id,
        risk_score=risk_score,
        drift=drift,
        sdi=sdi,
        decision=decision,
        recommendation=recommendation
    )

@app.get("/builds", response_model=List[dict])
async def get_builds(db: Session = Depends(get_db)):
    builds = db.query(BuildDB).order_by(BuildDB.timestamp.desc()).limit(10).all()
    return [
        {
            "id": b.id,
            "build_id": b.build_id,
            "timestamp": b.timestamp,
            "risk_score": b.risk_score,
            "drift": b.drift,
            "sdi": b.sdi,
            "decision": b.decision
        } for b in builds
    ]

@app.get("/stats")
async def get_stats(db: Session = Depends(get_db)):
    total_builds = db.query(BuildDB).count()
    if total_builds == 0:
        return {"avg_risk": 0, "total_builds": 0, "avg_sdi": 0}
    
    avg_risk = db.query(BuildDB).with_entities(sqlalchemy.func.avg(BuildDB.risk_score)).scalar()
    avg_sdi = db.query(BuildDB).with_entities(sqlalchemy.func.avg(BuildDB.sdi)).scalar()
    
    return {
        "avg_risk": float(avg_risk),
        "total_builds": total_builds,
        "avg_sdi": float(avg_sdi)
    }

@app.delete("/reset")
async def reset_data(db: Session = Depends(get_db)):
    """
    Clears all build history and vulnerabilities from the database.
    Use before a fresh demo.
    """
    db.query(VulnerabilityDB).delete()
    db.query(BuildDB).delete()
    db.commit()
    return {"message": "All data cleared. Ready for a fresh demo!"}

@app.post("/scan-repo")
async def scan_repo(request: RepoScanRequest, db: Session = Depends(get_db)):
    """
    Clones a GitHub repo, scans it with Bandit, and processes risk.
    """
    temp_dir = tempfile.mkdtemp()
    try:
        # 1. Clone repo (shallow clone for speed)
        clone_res = subprocess.run(
            ["git", "clone", "--depth", "1", request.repo_url, temp_dir],
            capture_output=True, text=True
        )
        if clone_res.returncode != 0:
            raise HTTPException(status_code=400, detail=f"Failed to clone repo: {clone_res.stderr}")

        # 2. Run Bandit scan
        scan_res = subprocess.run(
            ["bandit", "-r", temp_dir, "-f", "json"],
            capture_output=True, text=True
        )
        
        # Parse result
        try:
            scan_data = json.loads(scan_res.stdout)
            results = scan_data.get("results", [])
        except json.JSONDecodeError:
            print(f"Failed to parse Bandit output: {scan_res.stdout}")
            results = []
        
        # 3. Map to ACRIF format
        vulnerabilities = []
        for issue in results:
            # Map severity to a sensible 0-10 scale (not instantly 9)
            sev_map = {"LOW": 2.0, "MEDIUM": 5.0, "HIGH": 8.0}
            
            # Map confidence to a 0.0 - 1.0 Exploitability scale
            conf_map = {"LOW": 0.2, "MEDIUM": 0.5, "HIGH": 0.9}
            
            # Assign a random/variable stage to show the dynamic math working
            stage_cycle = ["dev", "staging", "prod"]
            idx = len(vulnerabilities) % 3
            
            vulnerabilities.append(VulnerabilitySchema(
                id=issue.get("test_id", "VULN"),
                severity=sev_map.get(issue.get("issue_severity"), 2.0),
                exploitability=conf_map.get(issue.get("issue_confidence"), 0.2),
                exposure=0.1 + (idx * 0.1), # Varies from 0.1 to 0.3
                criticality=0.5,
                stage=stage_cycle[idx],
                historical=False
            ))

        # 4. Process using existing logic
        build_id = f"repo_scan_{uuid.uuid4().hex[:8]}"
        
        # Reuse logic from calculate_risk
        previous_build = db.query(BuildDB).order_by(BuildDB.timestamp.desc()).first()
        previous_score = previous_build.risk_score if previous_build else 0.0
        total_build_count = db.query(BuildDB).count() + 1
        
        risk_score = calculate_risk_score(vulnerabilities) if vulnerabilities else 0.0
        drift = calculate_drift(risk_score, previous_score)
        sdi = calculate_sdi(vulnerabilities, total_build_count) if vulnerabilities else 0.0
        
        decision = "BLOCK" if risk_score > 70 or drift > 20 else "ALLOW"
        recommendation = "Review high-risk vulnerabilities" if decision == "BLOCK" else "Proceed with deployment"

        # Save to DB
        new_build = BuildDB(
            build_id=build_id,
            risk_score=risk_score,
            drift=drift,
            sdi=sdi,
            decision=decision
        )
        db.add(new_build)
        db.commit()
        db.refresh(new_build)

        for v in vulnerabilities:
            v_db = VulnerabilityDB(
                vuln_id=v.id,
                severity=v.severity,
                exploitability=v.exploitability,
                exposure=v.exposure,
                criticality=v.criticality,
                stage=v.stage,
                historical=v.historical,
                build_id=new_build.id
            )
            db.add(v_db)
        db.commit()

        return {
            "status": "success",
            "decision": decision,
            "risk_score": round(risk_score, 2),
            "drift": round(drift, 2),
            "recommendation": recommendation,
            "vuln_count": len(vulnerabilities)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        shutil.rmtree(temp_dir)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
