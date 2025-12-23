#!/usr/bin/env python3
"""
AI Job Hunter - Start Script
Run this to start the application
"""

import subprocess
import sys
import os
import time

def check_ollama():
    """Check if Ollama is running"""
    try:
        import requests
        response = requests.get("http://localhost:11434/api/tags", timeout=2)
        if response.status_code == 200:
            return True
    except:
        pass
    return False

def check_ollama_models():
    """Check available models"""
    try:
        import requests
        response = requests.get("http://localhost:11434/api/tags", timeout=2)
        if response.status_code == 200:
            data = response.json()
            if data.get('models'):
                print("Available models:")
                for model in data['models']:
                    print(f"  - {model.get('name', 'unknown')}")
                return True
    except:
        pass
    return False

def main():
    print("=" * 60)
    print("AI JOB HUNTER - Free Local LLM Version")
    print("=" * 60)
    print()
    
    # Check Ollama
    print("[1/3] Checking Ollama service...")
    if not check_ollama():
        print("❌ Ollama is not running!")
        print()
        print("Please start Ollama:")
        print("  - Windows: Run Ollama from Start Menu or double-click Ollama.exe")
        print("  - Or in PowerShell: ollama serve")
        print()
        print("Then run this script again.")
        sys.exit(1)
    
    print("✅ Ollama is running")
    
    # Check models
    print("[2/3] Checking AI models...")
    if not check_ollama_models():
        print("⚠️  No models found. Downloading default model...")
        print("   This will take ~2-5 minutes")
        os.system("ollama pull phi")
    else:
        print("✅ Models available")
    
    # Start FastAPI
    print("[3/3] Starting API server...")
    print()
    print("=" * 60)
    print("Server starting at: http://localhost:8000")
    print("API documentation: http://localhost:8000/docs")
    print("=" * 60)
    print()
    
    try:
        subprocess.run(
            [sys.executable, "-m", "uvicorn", "app.main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"],
            check=False
        )
    except KeyboardInterrupt:
        print()
        print("Server stopped.")
        sys.exit(0)

if __name__ == "__main__":
    main()
