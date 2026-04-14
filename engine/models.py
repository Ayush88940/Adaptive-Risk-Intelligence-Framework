from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

# SQLAlchemy Models
class BuildDB(Base):
    __tablename__ = "builds"
    id = Column(Integer, primary_key=True, index=True)
    build_id = Column(String, unique=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    risk_score = Column(Float)
    baseline_score = Column(Float)
    drift = Column(Float)
    sdi = Column(Float)
    decision = Column(String)
    
    vulnerabilities = relationship("VulnerabilityDB", back_populates="build")

class VulnerabilityDB(Base):
    __tablename__ = "vulnerabilities"
    id = Column(Integer, primary_key=True, index=True)
    vuln_id = Column(String) # e.g., CVE-xxx
    category = Column(String, nullable=True)
    description = Column(String, nullable=True)
    file_path = Column(String, nullable=True)
    line_number = Column(Integer, nullable=True)
    severity = Column(Float)
    exploitability = Column(Float)
    exposure = Column(Float)
    criticality = Column(Float)
    stage = Column(String)
    historical = Column(Boolean)
    build_id = Column(Integer, ForeignKey("builds.id"))
    
    build = relationship("BuildDB", back_populates="vulnerabilities")

# Pydantic Models (Schemas)
class VulnerabilitySchema(BaseModel):
    id: str
    category: Optional[str] = "General"
    description: Optional[str] = "No description provided"
    file_path: Optional[str] = "unknown"
    line_number: Optional[int] = 0
    severity: float  # CVSS Score
    exploitability: float
    exposure: float
    criticality: float
    stage: str
    historical: bool

class RiskRequest(BaseModel):
    build_id: str
    vulnerabilities: List[VulnerabilitySchema]

class RiskResponse(BaseModel):
    build_id: str
    risk_score: float
    baseline_score: float
    drift: float
    sdi: float
    decision: str
    recommendation: str
