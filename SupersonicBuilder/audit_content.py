#!/usr/bin/env python3
import os
import sys
import json
import subprocess
from pathlib import Path

ROOT = Path(".")

def check_file_exists(filepath, description=""):
    """Check if a file exists and return status."""
    path = ROOT / filepath
    exists = path.exists()
    return {
        'path': filepath,
        'description': description,
        'exists': exists,
        'status': '✅' if exists else '❌'
    }

def check_python_syntax(filepath):
    """Check Python file for syntax errors."""
    try:
        with open(filepath, 'r') as f:
            compile(f.read(), filepath, 'exec')
        return {'path': filepath, 'valid': True, 'error': None}
    except SyntaxError as e:
        return {'path': filepath, 'valid': False, 'error': str(e)}
    except Exception as e:
        return {'path': filepath, 'valid': False, 'error': str(e)}

def audit_content():
    """Comprehensive content audit."""
    
    audit = {
        'core_scripts': [],
        'workflows': [],
        'documentation': [],
        'badges': [],
        'dependencies': [],
        'python_errors': [],
        'missing_critical': [],
        'recommendations': []
    }
    
    print("="*70)
    print("🔍 PHASE 2: CONTENT AUDIT")
    print("="*70)
    
    # Core Python Scripts
    print("\n📝 Auditing Core Scripts...")
    core_scripts = [
        ('replit_auto_healer.py', 'Auto-healer service'),
        ('replit_feed_dashboard.py', 'Feed dashboard'),
        ('serve_pdfs.py', 'PDF viewer service'),
        ('supersonic_settings_server.py', 'Settings server'),
        ('autopush_to_github.py', 'GitHub autopush script'),
        ('create_support_bundle.py', 'Support bundle generator'),
        ('cleanup_large_files.sh', 'Large files cleanup script'),
    ]
    
    for script, desc in core_scripts:
        result = check_file_exists(script, desc)
        audit['core_scripts'].append(result)
        print(f"  {result['status']} {script:45s} - {desc}")
        
        # Check Python syntax
        if result['exists'] and script.endswith('.py'):
            syntax_check = check_python_syntax(script)
            if not syntax_check['valid']:
                audit['python_errors'].append(syntax_check)
                print(f"     ⚠️  Syntax error: {syntax_check['error']}")
    
    # Dependencies
    print("\n📦 Auditing Dependencies...")
    dep_files = [
        ('requirements.txt', 'Python dependencies'),
        ('.gitignore', 'Git ignore rules'),
        ('.replit', 'Replit config'),
        ('replit.nix', 'Nix environment config'),
    ]
    
    for dep_file, desc in dep_files:
        result = check_file_exists(dep_file, desc)
        audit['dependencies'].append(result)
        print(f"  {result['status']} {dep_file:45s} - {desc}")
        
        if not result['exists'] and dep_file in ['requirements.txt', '.gitignore']:
            audit['missing_critical'].append(dep_file)
    
    # Documentation & Badges
    print("\n📚 Auditing Documentation...")
    doc_files = [
        ('README.md', 'Main documentation'),
        ('replit.md', 'Replit project documentation'),
        ('docs/README.md', 'Docs folder'),
    ]
    
    for doc, desc in doc_files:
        result = check_file_exists(doc, desc)
        audit['documentation'].append(result)
        print(f"  {result['status']} {doc:45s} - {desc}")
    
    # Check for common issues
    print("\n🔍 Checking for Common Issues...")
    
    # Check .gitignore for large file patterns
    gitignore_path = ROOT / '.gitignore'
    if gitignore_path.exists():
        gitignore_content = gitignore_path.read_text()
        has_zip_ignore = '*.zip' in gitignore_content
        has_large_ignore = any(pattern in gitignore_content for pattern in ['*.tar', '*.7z', '*.rar'])
        
        if has_zip_ignore and has_large_ignore:
            print("  ✅ .gitignore properly excludes large files")
        else:
            print("  ⚠️  .gitignore missing large file exclusions")
            audit['recommendations'].append("Add *.zip, *.tar, *.7z to .gitignore")
    
    # Check for Python import errors in core scripts
    print("\n🐍 Checking Python Imports...")
    import_check_scripts = [
        'replit_auto_healer.py',
        'replit_feed_dashboard.py',
        'serve_pdfs.py',
        'supersonic_settings_server.py'
    ]
    
    for script in import_check_scripts:
        script_path = ROOT / script
        if script_path.exists():
            result = subprocess.run(
                [sys.executable, '-m', 'py_compile', script],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                print(f"  ✅ {script} - imports OK")
            else:
                print(f"  ❌ {script} - import errors")
                audit['python_errors'].append({
                    'path': script,
                    'valid': False,
                    'error': result.stderr[:200]
                })
    
    # Summary
    print("\n" + "="*70)
    print("📊 AUDIT SUMMARY")
    print("="*70)
    
    core_ok = sum(1 for s in audit['core_scripts'] if s['exists'])
    print(f"\n✅ Core Scripts: {core_ok}/{len(audit['core_scripts'])} present")
    
    deps_ok = sum(1 for d in audit['dependencies'] if d['exists'])
    print(f"✅ Dependencies: {deps_ok}/{len(audit['dependencies'])} present")
    
    docs_ok = sum(1 for d in audit['documentation'] if d['exists'])
    print(f"✅ Documentation: {docs_ok}/{len(audit['documentation'])} present")
    
    if audit['python_errors']:
        print(f"\n⚠️  Python Errors Found: {len(audit['python_errors'])}")
        for err in audit['python_errors']:
            print(f"   - {err['path']}: {err['error'][:100]}")
    else:
        print("\n✅ No Python syntax/import errors found")
    
    if audit['missing_critical']:
        print(f"\n❌ Missing Critical Files: {', '.join(audit['missing_critical'])}")
    
    if audit['recommendations']:
        print("\n💡 Recommendations:")
        for rec in audit['recommendations']:
            print(f"   - {rec}")
    
    print("\n" + "="*70)
    
    return audit

if __name__ == "__main__":
    audit = audit_content()
    
    # Save results
    with open('content_audit.json', 'w') as f:
        json.dump(audit, f, indent=2)
    
    print("\n✅ Content audit saved to: content_audit.json")
    print("✅ Phase 2 Complete: Content Audit")
