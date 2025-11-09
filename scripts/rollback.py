#!/usr/bin/env python3
"""
Rolls back the repository to a specified git tag or last known good release.
"""
import subprocess, sys

def rollback(tag=None):
    try:
        tag = tag or subprocess.check_output(["git", "describe", "--tags", "--abbrev=0"]).decode().strip()
        print(f"Rolling back to {tag} ...")
        subprocess.run(["git", "checkout", tag], check=True)
        print("Rollback complete ✅")
        return 0
    except subprocess.CalledProcessError as e:
        print(f"❌ Rollback failed: {e}")
        return 1
    except Exception as e:
        print(f"❌ Error during rollback: {e}")
        return 1

if __name__ == "__main__":
    tag = sys.argv[1] if len(sys.argv) > 1 else None
    sys.exit(rollback(tag))
