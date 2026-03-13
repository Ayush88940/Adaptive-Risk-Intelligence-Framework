import pytest
from engine.scoring import calculate_risk_score, calculate_drift, calculate_sdi
from engine.models import Vulnerability

def test_risk_score_calculation():
    # Scenario: High risk vulnerability
    v1 = Vulnerability(
        id="CVE-2024-1234",
        severity=9.0,
        exploitability=0.9,
        exposure=1.0,
        criticality=1.0,
        stage="prod",
        historical=True
    )
    
    score = calculate_risk_score([v1])
    assert score > 0
    assert score <= 100
    print(f"High risk score: {score}")

def test_drift_calculation():
    current = 75.0
    previous = 40.0
    drift = calculate_drift(current, previous)
    assert drift == 35.0

def test_sdi_calculation():
    v1 = Vulnerability(id="1", severity=5.0, exploitability=0.5, exposure=0.5, criticality=0.5, stage="dev", historical=False)
    v2 = Vulnerability(id="2", severity=7.0, exploitability=0.5, exposure=0.5, criticality=0.5, stage="dev", historical=False)
    
    sdi = calculate_sdi([v1, v2], 1)
    assert sdi == 12.0
    
    sdi_2_builds = calculate_sdi([v1, v2], 2)
    assert sdi_2_builds == 6.0
