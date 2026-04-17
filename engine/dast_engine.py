import httpx
from typing import List
from .models import VulnerabilitySchema
import uuid

async def run_dast_scan(live_url: str) -> List[VulnerabilitySchema]:
    """
    Performs a lightweight Dynamic Analysis (DAST) prober on a live URL.
    Checks for headers, SSL, and common exposed project files.
    """
    if not live_url:
        return []
    
    # Sanitize URL
    if not live_url.startswith(("http://", "https://")):
        live_url = f"https://{live_url}"
    
    vulnerabilities = []
    
    async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
        try:
            # 1. Check Security Headers
            response = await client.get(live_url)
            headers = response.headers
            
            checks = {
                "Strict-Transport-Security": "Missing HSTS Header (High)",
                "Content-Security-Policy": "Missing Content-Security-Policy (Medium)",
                "X-Frame-Options": "Missing Clickjacking Protection (Medium)",
                "X-Content-Type-Options": "Missing MIME-Sniffing Protection (Low)"
            }
            
            for header, msg in checks.items():
                if header not in headers:
                    vulnerabilities.append(VulnerabilitySchema(
                        id=f"DAST_HEADER_{header.replace('-', '_')}",
                        category="Missing Security Header",
                        description=f"{msg}. Response headers: {list(headers.keys())}",
                        severity=3.0 if "Low" in msg else (5.0 if "Medium" in msg else 8.0),
                        exploitability=0.7,
                        exposure=0.9, # Publicly accessible
                        criticality=0.6,
                        stage="prod",
                        historical=False,
                        analysis_type="DAST"
                    ))
            
            # 2. Check for Exposed Secrets / Configs
            secret_paths = [
                (".env", "Exposed Environment File (Critical)", 9.0),
                (".git/config", "Exposed Git Repository (Critical)", 9.5),
                ("package.json", "Exposed Node configuration (Medium)", 4.0),
                ("settings.py", "Exposed Django settings (High)", 7.0),
                ("phpinfo.php", "Exposed PHP Info (Medium)", 5.0)
            ]
            
            for path, msg, sev in secret_paths:
                test_url = f"{live_url.rstrip('/')}/{path}"
                try:
                    s_res = await client.get(test_url)
                    if s_res.status_code == 200 and len(s_res.text) > 0:
                        vulnerabilities.append(VulnerabilitySchema(
                            id=f"DAST_EXPOSED_{path.upper().replace('.', '_')}",
                            category="Information Leakage",
                            description=f"{msg} found at {test_url}",
                            severity=sev,
                            exploitability=0.9, # Already exposed
                            exposure=1.0,
                            criticality=0.8,
                            stage="prod",
                            historical=False,
                            analysis_type="DAST"
                        ))
                except:
                    continue

        except Exception as e:
            # If server is down, we return a "Service Down" vulnerability
            vulnerabilities.append(VulnerabilitySchema(
                id="DAST_CONNECT_ERROR",
                category="Service Availability",
                description=f"Could not connect to live URL for DAST scanning: {str(e)}",
                severity=2.0,
                exploitability=0.1,
                exposure=0.0,
                criticality=0.5,
                stage="prod",
                historical=False,
                analysis_type="DAST"
            ))

    return vulnerabilities
