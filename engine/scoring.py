from typing import List
from .models import VulnerabilitySchema

def calculate_risk_score(vulnerabilities: List[VulnerabilitySchema]) -> float:
    """
    R = Base Risk * Adaptive Factor
    Base Risk: (Severity * 0.5) + (Exploitability * 0.5)
    Adaptive Factor: 1.0 + Stage_Context + Exposure_Context
    """
    if not vulnerabilities:
        return 0.0
    
    total_score = 0.0
    for v in vulnerabilities:
        s = v.severity # 0-10 scale
        e = v.exploitability * 10 # 0-10 scale
        
        # Base Risk calculation (easy math)
        base_risk = (s * 0.5) + (e * 0.5)
        
        # Adaptive Factor calculation based on context
        # Stage: Dev=0.1, Staging=0.2, Prod=0.5
        d_map = {"dev": 0.1, "staging": 0.2, "prod": 0.5}
        d_context = d_map.get(v.stage.lower(), 0.5)
        
        # Exposure: High exposure means higher penalty
        exposure_context = v.exposure * 0.3  # scales 0 to 0.3
        
        adaptive_factor = 1.0 + d_context + exposure_context
        
        # Final individual score (scaled directly to 100 with * 10)
        r_i = (base_risk * 10) * adaptive_factor
        total_score += r_i
        
    # Final normalization (sum of averages, capped at 100)
    avg_score = total_score / len(vulnerabilities)
    return min(100.0, avg_score)

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
