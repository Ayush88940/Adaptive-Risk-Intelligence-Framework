from typing import List
from .models import VulnerabilitySchema

def calculate_risk_score(vulnerabilities: List[VulnerabilitySchema]) -> float:
    """
    R = Σ(wi × fi)
    Normalized weights:
    S (Severity): 0.3
    E (Exploit): 0.2
    X (Exposure): 0.15
    C (Criticality): 0.15
    D (Stage): 0.1
    H (Historical): 0.1
    """
    if not vulnerabilities:
        return 0.0
    
    total_score = 0.0
    for v in vulnerabilities:
        # fi mapping: Scale everything to 0-10 scale
        s = v.severity # Already 0-10
        e = v.exploitability * 10
        x = v.exposure * 10
        c = v.criticality * 10
        
        # d mapping: Dev=5, Staging=8, Prod=10
        d_map = {"dev": 5, "staging": 8, "prod": 10}
        d = d_map.get(v.stage.lower(), 10)
        
        h = 10 if v.historical else 5
        
        # Individual vuln risk (0-10 scale)
        r_i = (0.3 * s) + (0.2 * e) + (0.15 * x) + (0.15 * c) + (0.1 * d) + (0.1 * h)
        total_score += r_i
        
    # Final normalization (sum of averages, then scale to 0-100)
    avg_score = total_score / len(vulnerabilities)
    return min(100.0, avg_score * 10)

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
