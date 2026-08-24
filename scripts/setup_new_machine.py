#!/usr/bin/env python3
"""
Setup script for new machines.
This script helps you set up the ComicPlatform project on a new computer.
"""
import sys
import subprocess
import os
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

def run_command(cmd, description):
    """Run a shell command and print status."""
    print(f"\n{'='*60}")
    print(f"Step: {description}")
    print(f"Command: {cmd}")
    print('='*60)
    
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    if result.returncode == 0:
        print(f"[OK] {description} completed successfully")
        if result.stdout:
            print(result.stdout)
    else:
        print(f"[ERR] {description} failed")
        if result.stderr:
            print(result.stderr)
        return False
    return True


def main():
    print("="*60)
    print("ComicPlatform - New Machine Setup")
    print("="*60)
    
    # Check prerequisites
    print("\nChecking prerequisites...")
    
    # Check Node.js
    try:
        result = subprocess.run("node --version", shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"[OK] Node.js found: {result.stdout.strip()}")
        else:
            print("[ERR] Node.js not found. Please install Node.js 18+ from https://nodejs.org/")
            sys.exit(1)
    except Exception as e:
        print(f"[ERR] Error checking Node.js: {e}")
        sys.exit(1)
    
    # Check npm
    try:
        result = subprocess.run("npm --version", shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"[OK] npm found: {result.stdout.strip()}")
        else:
            print("[ERR] npm not found")
            sys.exit(1)
    except Exception as e:
        print(f"[ERR] Error checking npm: {e}")
        sys.exit(1)
    
    # Check Python
    try:
        result = subprocess.run("python --version", shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"[OK] Python found: {result.stdout.strip()}")
        else:
            print("[ERR] Python not found. Please install Python 3.8+ from https://python.org/")
            sys.exit(1)
    except Exception as e:
        print(f"[ERR] Error checking Python: {e}")
        sys.exit(1)
    
    # Check psycopg2
    try:
        import psycopg2
        print("[OK] psycopg2 found")
    except ImportError:
        print("[INFO] psycopg2 not found. Installing...")
        if not run_command("pip install psycopg2-binary", "Install psycopg2"):
            print("[WARN] Failed to install psycopg2. You may need it for database scripts.")
    
    # Get project root
    script_dir = Path(__file__).parent
    project_root = script_dir.parent.parent
    web_dir = project_root / "web"
    
    print(f"\nProject root: {project_root}")
    print(f"Web directory: {web_dir}")
    
    # Change to web directory
    os.chdir(web_dir)
    print(f"Changed to directory: {os.getcwd()}")
    
    # Install npm dependencies
    if not run_command("npm install", "Install npm dependencies"):
        print("[ERR] Failed to install dependencies")
        sys.exit(1)
    
    # Generate Prisma client
    if not run_command("npm run db:generate", "Generate Prisma client"):
        print("[ERR] Failed to generate Prisma client")
        sys.exit(1)
    
    # Check for .env.local
    env_file = web_dir / ".env.local"
    if not env_file.exists():
        print("\n" + "="*60)
        print("SETUP REQUIRED: Environment Variables")
        print("="*60)
        print("\nPlease create .env.local file with your Supabase credentials.")
        print("You can copy from .env.example and fill in the values:")
        print("\n  cp .env.example .env.local")
        print("\nRequired variables:")
        print("  - NEXT_PUBLIC_APP_URL")
        print("  - DATABASE_URL")
        print("  - NEXT_PUBLIC_SUPABASE_URL")
        print("  - NEXT_PUBLIC_SUPABASE_ANON_KEY")
        print("\nGet these from your Supabase project:")
        print("  1. Project Settings → Database → Connection string")
        print("  2. Project Settings → API → Project URL & anon key")
        print("="*60)
    else:
        print("\n[OK] .env.local found")
        
        # Try to push schema
        print("\nAttempting to push schema to database...")
        if run_command("npm run db:push", "Push schema to database"):
            print("[OK] Database schema synced")
        else:
            print("[WARN] Failed to push schema. Check your DATABASE_URL in .env.local")
    
    print("\n" + "="*60)
    print("Setup Complete!")
    print("="*60)
    print("\nNext steps:")
    print("1. Ensure .env.local is configured with your Supabase credentials")
    print("2. Run: npm run db:push")
    print("3. Run: npm run dev")
    print("4. Visit: http://localhost:3001")
    print("\nFor production deployment, see DEPLOY.md")
    print("="*60)


if __name__ == "__main__":
    main()
