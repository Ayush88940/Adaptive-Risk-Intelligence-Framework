from typing import List
from fastapi import FastAPI, HTTPException, Depends
import uvicorn
import sqlalchemy
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
from .models import VulnerabilitySchema, RiskRequest, RiskResponse, BuildDB, VulnerabilityDB
from .scoring import calculate_risk_score, calculate_drift, calculate_sdi
from .database import engine, Base, get_db

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Adaptive Context-Aware Risk Intelligence API")

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
    return {"message": "Adaptive Context-Aware Risk Intelligence Engine is running"}

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
    
    decision = "BLOCK" if risk_score > 70 or abs(drift) > 20 else "ALLOW"
    recommendation = "Review high-risk vulnerabilities" if decision == "BLOCK" else "Proceed with deployment"
    
    # 4. Save to Database
    new_build = BuildDB(
        build_id=request.build_id,
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

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
