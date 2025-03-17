#!/usr/bin/env python

import os
import sys
import subprocess
import argparse

def run_test(test_name=None):
    if test_name:
        if test_name == "all":
            cmd = [sys.executable, "scripts/test_all.py"]
        else:
            script_path = f"scripts/test_{test_name}.py"
            if not os.path.exists(script_path):
                print(f"Error: Test script {script_path} not found")
                return False
            cmd = [sys.executable, script_path]
    else:
        cmd = [sys.executable, "scripts/fix_test.py"]
    
    try:
        return subprocess.run(cmd, check=True).returncode == 0
    except subprocess.CalledProcessError:
        return False
    except KeyboardInterrupt:
        print("\nTest interrupted by user.")
        return False

def main():
    parser = argparse.ArgumentParser(description='Run Gmail App tests')
    parser.add_argument('test', nargs='?', default=None, 
                      help='Test to run (whatsapp, notifications, email_checks, all)')
    
    args = parser.parse_args()
    
    print("\n==================================================")
    print("            Gmail App Test Launcher               ")
    print("==================================================\n")
    
    if args.test:
        print(f"Running test: {args.test}\n")
        success = run_test(args.test)
    else:
        print("No test specified. Running configuration check.\n")
        success = run_test()
        
        if success:
            print("\nWhich test would you like to run?")
            print("1. WhatsApp Test")
            print("2. Notifications Test")
            print("3. Email Check Test")
            print("4. All Tests")
            print("5. Exit")
            
            choice = input("\nEnter your choice (1-5): ").strip()
            
            test_map = {
                "1": "whatsapp",
                "2": "notifications",
                "3": "email_checks",
                "4": "all"
            }
            
            if choice in test_map:
                success = run_test(test_map[choice])
            else:
                print("Exiting...")
                return
    
    print("\n==================================================")
    print(f"Test result: {'✅ PASS' if success else '❌ FAIL'}")
    print("==================================================")

if __name__ == "__main__":
    main()
