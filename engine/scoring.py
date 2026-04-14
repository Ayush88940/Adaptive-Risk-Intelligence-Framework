from typing import List
from .models import VulnerabilitySchema
from .ahp import get_adaptive_weights

def calculate_risk_score(vulnerabilities: List[VulnerabilitySchema]) -> float:
    """
    R = Σ (Weight_i * Value_i)
    Weights are derived from AHP: [Severity, Exploitability, Stage, Exposure]
    """
    if not vulnerabilities:
        return 0.0
    
    weights = get_adaptive_weights()
    total_score = 0.0
    
    for v in vulnerabilities:
        # Normalize variables to 0-10 scale
        s = v.severity 
        e = v.exploitability * 10
        
        # Map stage to numeric values: dev=2, staging=5, prod=10
        stage_map = {"dev": 2.0, "staging": 5.0, "prod": 10.0}
        st = stage_map.get(v.stage.lower(), 10.0)
        
        ex = v.exposure * 10 # scale 0-1 to 0-10
        
        # Weighted calculation
        r_i = (s * weights["severity"]) + \
              (e * weights["exploitability"]) + \
              (st * weights["stage"]) + \
              (ex * weights["exposure"])
        
        # Rescale from 0-10 back to 1-100 for the final score
        total_score += (r_i * 10)
        
    avg_score = total_score / len(vulnerabilities)
    return min(100.0, avg_score)

def calculate_baseline_score(vulnerabilities: List[VulnerabilitySchema]) -> float:
    """
    Baseline Risk (CVSS-only): (Severity * 0.5 + Exploitability * 0.5) * 10
    Used for comparison in research paper to show 'Alert Fatigue' reduction.
    """
    if not vulnerabilities:
        return 0.0
    
    total_score = 0.0
    for v in vulnerabilities:
        s = v.severity
        e = v.exploitability * 10
        total_score += ((s * 0.5) + (e * 0.5)) * 10
        
    return min(100.0, total_score / len(vulnerabilities))

def calculate_drift(current_score: float, previous_score: float) -> float:
    """
    Drift = R(current) - R(previous)
    """
    return current_score - previous_score

def calculate_sdi(vulnerabilities: List[VulnerabilitySchema], total_builds: int) -> float:
    """
    SDI = Σ(weighted vulnerabilities) / total builds
    """
    if total_builds == 0:
        return 0.0
    
    # Weighted vulnerabilities = Sum of severity for SDI calculation per roadmap
    weighted_sum = sum(v.severity for v in vulnerabilities)
    return weighted_sum / total_builds
