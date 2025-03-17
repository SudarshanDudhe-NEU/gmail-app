#!/usr/bin/env python

import os
import sys
import subprocess
import time

# Ensure logs directory exists
os.makedirs('logs', exist_ok=True)

def run_test(script_name):
    """Run a test script and return result"""
    print(f"\n\033[1;34mRunning {script_name}...\033[0m")
    
    try:
        result = subprocess.run(
            [sys.executable, f"scripts/{script_name}"],
            check=True,
            capture_output=False
        )
        return result.returncode == 0
    except subprocess.CalledProcessError:
        return False

def fix_permissions():
    """Fix permissions on scripts"""
    print("\n\033[1;34mFixing script permissions...\033[0m")
    for script in os.listdir('scripts'):
        if script.endswith('.py'):
            os.chmod(f"scripts/{script}", 0o755)
    
    # Also fix main scripts
    for script in ['app.py', 'check_old_emails.py', 'run_app.sh']:
        if os.path.exists(script):
            os.chmod(script, 0o755)
            
    print("✅ Permissions fixed")

def main():
    """Main runner function"""
    print("\n\033[1;32m===================================\033[0m")
    print("\033[1;32m     Gmail App Test Runner         \033[0m")
    print("\033[1;32m===================================\033[0m")
    
    # Fix permissions
    fix_permissions()
    
    # Run specific tests
    tests = [
        ('fix_test.py', 'Configuration Test'),
        ('test_whatsapp.py', 'WhatsApp Test'),
        ('test_notifications.py', 'Notification Test'),
        ('test_email_checks.py', 'Email Check Test')
    ]
    
    results = {}
    
    for script, description in tests:
        results[description] = run_test(script)
        # Add a small delay between tests
        time.sleep(1)
    
    # Print results
    print("\n\033[1;32m===================================\033[0m")
    print("\033[1;32m           Test Results            \033[0m")
    print("\033[1;32m===================================\033[0m")
    
    for description, success in results.items():
        status = "\033[1;32m✅ PASS\033[0m" if success else "\033[1;31m❌ FAIL\033[0m"
        print(f"{description}: {status}")
    
    print("\n\033[1;32m===================================\033[0m")
    
    # Run the main app for a short time if all tests passed
    if all(results.values()):
        print("\nAll tests passed! Would you like to run the application? (y/n)")
        choice = input("> ").strip().lower()
        
        if choice == 'y':
            print("\n\033[1;34mStarting the application...\033[0m")
            print("(Press Ctrl+C to stop after testing)\n")
            
            try:
                subprocess.run([sys.executable, "app.py"], check=True)
            except KeyboardInterrupt:
                print("\n\033[1;34mApplication stopped.\033[0m")
            except subprocess.CalledProcessError:
                print("\n\033[1;31mApplication exited with an error.\033[0m")

if __name__ == "__main__":
    main()