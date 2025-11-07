#!/usr/bin/env python3
"""
Health Feed Generator for GitHub Actions
Generates docs/status/health.json with build metadata
"""

import json
import os
import datetime

def main():
    """Generate health feed JSON"""
    data = {
        "build_id": os.getenv("GITHUB_RUN_NUMBER", "local"),
        "commit": os.getenv("GITHUB_SHA", "local")[:8],
        "status": os.getenv("JOB_STATUS", "unknown"),
        "timestamp": datetime.datetime.utcnow().isoformat(),
        "artifacts_url": f"https://github.com/{os.getenv('GITHUB_REPOSITORY', 'unknown')}/actions/runs/{os.getenv('GITHUB_RUN_ID', 'unknown')}",
        "workflow": os.getenv("GITHUB_WORKFLOW", "unknown"),
        "branch": os.getenv("GITHUB_REF_NAME", "unknown"),
    }
    
    os.makedirs("docs/status", exist_ok=True)
    
    with open("docs/status/health.json", "w") as f:
        json.dump(data, f, indent=2)
    
    print("✅ Health feed updated:", json.dumps(data, indent=2))

if __name__ == "__main__":
    main()
