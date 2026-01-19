#!/usr/bin/env python
"""
Verify Railway MySQL deployment readiness.
Run this before deploying to Railway.
"""
import os
import sys


def check_file_exists(filepath, description):
    """Check if a file exists."""
    if os.path.exists(filepath):
        print(f"✅ {description}: {filepath}")
        return True
    else:
        print(f"❌ MISSING {description}: {filepath}")
        return False


def check_file_content(filepath, should_not_contain, description):
    """Check if file does NOT contain certain strings."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            for term in should_not_contain:
                if term.lower() in content.lower():
                    print(f"❌ {description} contains '{term}': {filepath}")
                    return False
        print(f"✅ {description} is clean: {filepath}")
        return True
    except Exception as e:
        print(f"⚠️  Could not read {filepath}: {e}")
        return False


def check_file_has_content(filepath, should_contain, description):
    """Check if file contains certain strings."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            for term in should_contain:
                if term not in content:
                    print(f"❌ {description} missing '{term}': {filepath}")
                    return False
        print(f"✅ {description} has required content: {filepath}")
        return True
    except Exception as e:
        print(f"⚠️  Could not read {filepath}: {e}")
        return False


def main():
    print("=" * 70)
    print("🔍 RAILWAY MYSQL DEPLOYMENT VERIFICATION")
    print("=" * 70)
    print()

    checks_passed = 0
    checks_total = 0

    # Check 1: Required files exist
    print("📦 Checking Required Files...")
    files_to_check = [
        ("requirements.txt", "Requirements file"),
        ("config.py", "Configuration file"),
        ("nixpacks.toml", "Nixpacks configuration"),
        ("railway.json", "Railway configuration"),
        ("wsgi.py", "WSGI entry point"),
        ("run.py", "Flask runner"),
    ]
    
    for filepath, desc in files_to_check:
        checks_total += 1
        if check_file_exists(filepath, desc):
            checks_passed += 1
    
    print()

    # Check 2: No PostgreSQL in requirements.txt
    print("🔍 Checking for PostgreSQL Dependencies...")
    checks_total += 1
    if check_file_content(
        "requirements.txt",
        ["psycopg2", "postgres"],
        "requirements.txt"
    ):
        checks_passed += 1
    
    print()

    # Check 3: PyMySQL in requirements.txt
    print("🔍 Checking for MySQL Dependencies...")
    checks_total += 1
    if check_file_has_content(
        "requirements.txt",
        ["PyMySQL"],
        "requirements.txt"
    ):
        checks_passed += 1
    
    print()

    # Check 4: nixpacks.toml configured correctly
    print("🔍 Checking nixpacks.toml configuration...")
    checks_total += 1
    if check_file_has_content(
        "nixpacks.toml",
        ["python39", "gcc"],
        "nixpacks.toml"
    ):
        checks_passed += 1
    
    checks_total += 1
    if check_file_content(
        "nixpacks.toml",
        ["postgresql"],
        "nixpacks.toml"
    ):
        checks_passed += 1
    
    print()

    # Check 5: Config.py has MySQL support
    print("🔍 Checking config.py for MySQL support...")
    checks_total += 1
    if check_file_has_content(
        "config.py",
        ["MYSQL_URL", "pymysql"],
        "config.py"
    ):
        checks_passed += 1
    
    print()

    # Check 6: .env is gitignored
    print("🔍 Checking .gitignore...")
    checks_total += 1
    if os.path.exists(".gitignore"):
        with open(".gitignore", 'r') as f:
            gitignore_content = f.read()
            if ".env" in gitignore_content:
                print("✅ .env is in .gitignore")
                checks_passed += 1
            else:
                print("⚠️  .env should be in .gitignore")
    else:
        print("⚠️  .gitignore not found")
    
    print()

    # Summary
    print("=" * 70)
    print(f"📊 VERIFICATION SUMMARY: {checks_passed}/{checks_total} checks passed")
    print("=" * 70)
    print()

    if checks_passed == checks_total:
        print("🎉 ALL CHECKS PASSED! Your code is ready for Railway deployment.")
        print()
        print("Next steps:")
        print("1. Commit and push your changes:")
        print("   git add .")
        print("   git commit -m 'Convert to MySQL for Railway deployment'")
        print("   git push origin main")
        print()
        print("2. Deploy to Railway:")
        print("   - Create project from GitHub repo")
        print("   - Add MySQL database")
        print("   - Set environment variables")
        print()
        print("📖 See DEPLOYMENT_CHECKLIST.md for detailed instructions")
        return 0
    else:
        print("⚠️  SOME CHECKS FAILED! Please fix the issues above.")
        print()
        if not os.path.exists("nixpacks.toml"):
            print("💡 TIP: nixpacks.toml is missing. This file prevents PostgreSQL installation.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
