#!/usr/bin/env python3
"""Script to start both frontend and backend services"""

import os
import subprocess
import sys
import time

# Get the project root directory
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

def start_backend():
    """Start the Django backend service"""
    print("Starting backend service...")
    backend_dir = os.path.join(PROJECT_ROOT, 'Server')
    venv_python = os.path.join(backend_dir, 'venv', 'bin', 'python3')
    
    # Run Django development server
    cmd = [
        venv_python, 
        'manage.py', 
        'runserver', 
        '0.0.0.0:8003'
    ]
    
    proc = subprocess.Popen(
        cmd,
        cwd=backend_dir,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )
    
    # Give it a moment to start
    time.sleep(2)
    
    if proc.poll() is None:
        print(f"Backend service started successfully (PID: {proc.pid})")
        return proc
    else:
        print(f"Backend failed to start. Exit code: {proc.returncode}")
        return None


def start_frontend():
    """Start the frontend SPA server"""
    print("Starting frontend service...")
    frontend_script = os.path.join(PROJECT_ROOT, 'Page', 'serve_spa.py')
    
    proc = subprocess.Popen(
        ['python3', frontend_script],
        cwd=os.path.join(PROJECT_ROOT, 'Page'),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )
    
    # Give it a moment to start
    time.sleep(2)
    
    if proc.poll() is None:
        print(f"Frontend service started successfully (PID: {proc.pid})")
        return proc
    else:
        print(f"Frontend failed to start. Exit code: {proc.returncode}")
        return None


def main():
    print("=" * 60)
    print("Starting WeWin services...")
    print("=" * 60)
    
    # Start backend
    backend_proc = start_backend()
    
    # Start frontend
    frontend_proc = start_frontend()
    
    if backend_proc and frontend_proc:
        print("\n" + "=" * 60)
        print("Both services are running!")
        print("- Frontend: http://localhost:8080")
        print("- Backend:  http://localhost:8003")
        print("\nPress Ctrl+C to stop all services")
        print("=" * 60)
        
        try:
            # Keep script running
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nStopping services...")
            if backend_proc:
                backend_proc.terminate()
            if frontend_proc:
                frontend_proc.terminate()
            print("Services stopped.")


if __name__ == "__main__":
    main()
