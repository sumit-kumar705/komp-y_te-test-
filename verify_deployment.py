#!/usr/bin/env python
"""
Final pre-deployment verification for Railway.
Run this before pushing to GitHub.
"""

import os
import sys


def check_file_exists(filepath, required=True):
    """Check if a file exists."""
    exists = os.path.exists(filepath)
    status = "✅" if exists else ("❌" if required else "⚠️")
    print(f"{status} {filepath}: {'EXISTS' if exists else 'MISSING'}")
    return exists


def check_file_not_exists(filepath, description):
    """Check if a file does NOT exist (should be deleted)."""
    exists = os.path.exists(filepath)
    status = "✅" if not exists else "❌"
    print(f"{status} {description}: {'DELETED' if not exists else 'STILL EXISTS - SHOULD BE DELETED!'}")
    return not exists


def check_file_content(filepath, should_contain=None, should_not_contain=None):
    """Check file content."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            
            if should_contain:
                for term in should_contain:
                    if term not in content:
                        print(f"  ❌ Missing required: '{term}'")
                        return False
                print(f"  ✅ Contains all required terms")
            
            if should_not_contain:
                for term in should_not_contain:
                    if term.lower() in content.lower():
                        print(f"  ❌ Contains forbidden: '{term}'")
                        return False
                print(f"  ✅ Clean (no forbidden terms)")
            
        return True
    except Exception as e:
        print(f"  ⚠️  Error reading file: {e}")
        return False


def main():
    print("=" * 80)
    print("🔍 RAILWAY DEPLOYMENT VERIFICATION - FINAL CHECK")
    print("=" * 80)
    print()
    
    checks_passed = 0
    checks_total = 0
    
    # 1. Check required files exist
    print("📦 REQUIRED FILES:")
    required_files = [
        "requirements.txt",
        "runtime.txt",
        "Procfile",
        "railway.json",
        "wsgi.py",
        "run.py",
        "config.py",
        "init_db.py",
        "app/__init__.py",
        "app/extensions.py",
    ]
    
    for filepath in required_files:
        checks_total += 1
        if check_file_exists(filepath, required=True):
            checks_passed += 1
    
    print()
    
    # 2. Check nixpacks.toml is DELETED
    print("🗑️  DELETED FILES (should not exist):")
    checks_total += 1
    if check_file_not_exists("nixpacks.toml", "nixpacks.toml"):
        checks_passed += 1
    print()
    
    # 3. Check requirements.txt
    print("📋 REQUIREMENTS.TXT:")
    checks_total += 2
    print("  Checking for PostgreSQL dependencies...")
    if check_file_content("requirements.txt", should_not_contain=["psycopg2", "psycopg"]):
        checks_passed += 1
    
    print("  Checking for MySQL dependencies...")
    if check_file_content("requirements.txt", should_contain=["PyMySQL"]):
        checks_passed += 1
    
    print()
    
    # 4. Check Procfile
    print("⚙️  PROCFILE:")
    checks_total += 1
    print("  Checking deployment command...")
    if check_file_content("Procfile", should_contain=["gunicorn", "wsgi:app"]):
        checks_passed += 1
    
    print()
    
    # 5. Check railway.json
    print("🚂 RAILWAY.JSON:")
    checks_total += 1
    print("  Checking configuration...")
    if check_file_content("railway.json", should_contain=["startCommand", "gunicorn"]):
        checks_passed += 1
    
    print()
    
    # 6. Check config.py
    print("⚙️  CONFIG.PY:")
    checks_total += 2
    print("  Checking for MySQL support...")
    if check_file_content("config.py", should_contain=["MYSQL_URL", "pymysql"]):
        checks_passed += 1
        
    print("  Checking no PostgreSQL references...")
    if check_file_content("config.py", should_not_contain=["psycopg", "postgresql://"]):
        checks_passed += 1
    
    print()
    
    # 7. Check Python syntax
    print("🐍 PYTHON SYNTAX:")
    checks_total += 1
    try:
        import py_compile
        py_compile.compile("wsgi.py", doraise=True)
        py_compile.compile("init_db.py", doraise=True)
        py_compile.compile("app/__init__.py", doraise=True)
        print("  ✅ All Python files compile successfully")
        checks_passed += 1
    except Exception as e:
        print(f"  ❌ Python syntax error: {e}")
    
    print()
    
    # Summary
    print("=" * 80)
    print(f"📊 FINAL SCORE: {checks_passed}/{checks_total} checks passed")
    print("=" * 80)
    print()
    
    if checks_passed == checks_total:
        print("🎉 PERFECT! Your code is 100% ready for Railway deployment!")
        print()
        print("✅ Next steps:")
        print("   1. git add .")
        print("   2. git commit -m 'Fix Railway build - Remove nixpacks, simplify deployment'")
        print("   3. git push origin main")
        print("   4. Deploy to Railway!")
        print()
        print("📖 See DEPLOY_RAILWAY_SIMPLE.md for detailed deployment instructions")
        return 0
    else:
        print("⚠️  SOME CHECKS FAILED!")
        print("Please fix the issues above before deploying to Railway.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
