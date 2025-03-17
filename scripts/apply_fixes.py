#!/usr/bin/env python

import os
import re
import sys

def fix_email_parser():
    """Fix email parser by adding settings import"""
    filepath = "utils/email_parser.py"
    print(f"Fixing {filepath}...")
    
    try:
        with open(filepath, 'r') as file:
            content = file.read()
            
        if 'import config.settings as settings' not in content:
            # Add settings import
            content = re.sub(
                r'import (re|logging)',
                'import \\1\nimport config.settings as settings',
                content,
                count=1
            )
            
            # Update is_important_email function to handle list/string properly
            content = re.sub(
                r'(def is_important_email.*?keywords = ).*?(\n\s+for keyword)',
                '\\1[k.lower() for k in settings.IMPORTANCE_KEYWORDS]\\2',
                content,
                flags=re.DOTALL
            )
            
            with open(filepath, 'w') as file:
                file.write(content)
                
            print(f"✅ Added settings import to {filepath}")
        else:
            print(f"✅ Settings import already exists in {filepath}")
    except Exception as e:
        print(f"❌ Error fixing {filepath}: {e}")

def fix_notification_service():
    """Fix notification_service.py to handle function calls properly"""
    filepath = "services/notification_service.py"
    print(f"Fixing {filepath}...")
    
    try:
        with open(filepath, 'r') as file:
            content = file.read()
        
        # Replace extract_job_details(body) with proper calls to specific functions
        content = re.sub(
            r'job_details = extract_job_details\(body\)',
            'job_title = extract_job_title(body)\n        company = extract_company(body)\n        location = extract_location(body)\n        salary = extract_salary(body)',
            content
        )
        
        # Check if we successfully replaced the problematic function call
        if 'extract_job_details(body)' not in content:
            with open(filepath, 'w') as file:
                file.write(content)
            print(f"✅ Fixed function calls in {filepath}")
        else:
            print(f"⚠️ Could not fix all issues in {filepath}")
    except Exception as e:
        print(f"❌ Error fixing {filepath}: {e}")

def fix_notification_test():
    """Fix test_notifications.py to include received_time parameter"""
    filepath = "scripts/test_notifications.py"
    print(f"Fixing {filepath}...")
    
    try:
        with open(filepath, 'r') as file:
            content = file.read()
        
        # Replace send_notification call with one that includes received_time
        if 'received_time=' not in content:
            import_time_added = False
            if 'import time' not in content:
                content = re.sub(
                    r'import (.*?)',
                    'import \\1\nimport time',
                    content,
                    count=1
                )
                import_time_added = True
                
            # Add received_time parameter
            content = re.sub(
                r'(result = notification_service.send_notification\([\s\S]*?sender=.*?)(\))',
                '\\1,\n        received_time=int(time.time() * 1000)\\2',
                content
            )
                
            with open(filepath, 'w') as file:
                file.write(content)
                
            print(f"✅ Added received_time parameter in {filepath}")
            if import_time_added:
                print(f"✅ Added time import in {filepath}")
        else:
            print(f"✅ received_time parameter already exists in {filepath}")
    except Exception as e:
        print(f"❌ Error fixing {filepath}: {e}")

def fix_test_all():
    """Fix test_all.py with proper function calls"""
    filepath = "scripts/test_all.py"
    print(f"Creating improved {filepath}...")
    
    content = """
    #!/usr/bin/env python

	import os
	import sys
	import logging
	import time

	# Add parent directory to path
	sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

	# Configure logging
	logging.basicConfig(
		level=logging.INFO,
		format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
	)
	logger = logging.getLogger(__name__)

	def test_whatsapp():
		#"Test WhatsApp functionality"
		print("\\n🔍 Testing WhatsApp Session...")
		
		try:
			from utils.whatsapp_notifications import (
				is_session_valid,
				send_whatsapp_message
			)
			
			session_valid = is_session_valid()
			
			if session_valid:
				print("✅ WhatsApp session is valid")
				
				print("\\n📱 Testing WhatsApp Messaging...")
				result = send_whatsapp_message(
					phone_number="917721976267",
					message="Test message from Gmail Monitor test suite",
					use_headless=True
				)
				
				if result:
					print("✅ WhatsApp message sent successfully")
					return True
				else:
					print("❌ Failed to send WhatsApp message")
					return False
			else:
				print("❌ WhatsApp session is not valid")
				print("   Run 'python scripts/initialize_whatsapp.py' to set up a session")
				return False
				
		except Exception as e:
			print(f"❌ Error testing WhatsApp: {e}")
			return False

	def test_notifications():
		""Test notification service""
		print("\\n📧 Testing Notifications...")
		
		try:
			from services.notification_service import NotificationService
			import config.settings as settings
			
			notification_service = NotificationService({
				'TELEGRAM_BOT_TOKEN': settings.TELEGRAM_BOT_TOKEN,
				'TELEGRAM_CHAT_ID': settings.TELEGRAM_CHAT_ID,
				'WHATSAPP_ENABLED': settings.WHATSAPP_ENABLED,
				'WHATSAPP_PHONE': settings.WHATSAPP_PHONE
			})
			
			# Use the correct parameter name: received_time
			result = notification_service.send_notification(
				subject="Test Subject",
				body="Test body from test_all.py",
				sender="test@example.com",
				received_time=int(time.time() * 1000)
			)
			
			if result:
				print("✅ Notification sent successfully")
				return True
			else:
				print("❌ Failed to send notification")
				return False
				
		except Exception as e:
			print(f"❌ Error testing notifications: {e}")
			return False

	def test_email():
		""Test email checking functionality""
		print("\\n📨 Testing Email Checking...")
		
		try:
			from auth.gmail_auth import gmail_authenticate
			from services.gmail_service import search_messages, get_message_details
			from utils.email_parser import extract_email_data, is_important_email
			import config.settings as settings  # Make sure to import settings
			
			# Authenticate
			service = gmail_authenticate()
			if not service:
				print("❌ Gmail authentication failed")
				return False
				
			print("✅ Gmail authentication successful")
			
			# Check for recent emails
			query = "newer_than:1d"
			print(f"Searching for emails with query: {query}")
			
			response = search_messages(service, query)
			if not response or 'messages' not in response:
				print("No emails found for testing")
				return True
				
			messages = response.get('messages', [])[:3]  # Get up to 3 emails
			print(f"Found {len(messages)} emails for testing")
			
			for message in messages:
				message_id = message.get('id')
				message_data = get_message_details(service, message_id)
				
				if message_data:
					email_data = extract_email_data(message_data)
					print(f"Email: {email_data['subject']}")
					
					# Check importance
					is_important = is_important_email(email_data)
					print(f"  Important: {'Yes' if is_important else 'No'}")
					
			print("✅ Email checking test completed successfully")
			return True
			
		except Exception as e:
			print(f"❌ Error testing email checking: {e}")
			return False

	def run_all_tests():
		""Run all tests""
		print("\\n==================================================")
		print("                  Test Suite                      ")
		print("==================================================")
		
		# Test WhatsApp
		whatsapp_ok = test_whatsapp()
		
		# Test notifications
		notifications_ok = test_notifications()
		
		# Test email
		email_ok = test_email()
		
		# Summary
		print("\\n==================================================")
		print("                 Test Results                     ")
		print("==================================================")
		print(f"WhatsApp:      {'✅ PASS' if whatsapp_ok else '❌ FAIL'}")
		print(f"Notifications: {'✅ PASS' if notifications_ok else '❌ FAIL'}")
		print(f"Email:         {'✅ PASS' if email_ok else '❌ FAIL'}")
		print("==================================================")
		
		# Overall result
		overall = all([whatsapp_ok, notifications_ok, email_ok])
		print(f"\\nOverall: {'✅ ALL TESTS PASSED' if overall else '❌ SOME TESTS FAILED'}")
		
		return overall

	if __name__ == "__main__":
		run_all_tests()
	"""
    
    try:
        with open(filepath, 'w') as file:
            file.write(content)
        print(f"✅ Created improved {filepath}")
    except Exception as e:
        print(f"❌ Error creating {filepath}: {e}")

def create_test_launcher():
    """Create a test launcher script"""
    filepath = "test.py"
    print(f"Creating {filepath}...")
    
    content = """
    #!/usr/bin/env python

	import os
	import sys
	import subprocess
	import argparse

	def run_test(test_name=None):
		""Run specified test or all tests""
		if test_name:
			if test_name == "all":
				# Run the all-in-one test script
				cmd = [sys.executable, "scripts/test_all.py"]
			else:
				# Run a specific test
				script_path = f"scripts/test_{test_name}.py"
				if not os.path.exists(script_path):
					print(f"Error: Test script {script_path} not found")
					return False
				cmd = [sys.executable, script_path]
		else:
			# Run the fix_test script
			cmd = [sys.executable, "scripts/fix_test.py"]
		
		try:
			return subprocess.run(cmd, check=True).returncode == 0
		except subprocess.CalledProcessError:
			return False
		except KeyboardInterrupt:
			print("\\nTest interrupted by user.")
			return False

	def main():
		parser = argparse.ArgumentParser(description='Run Gmail App tests')
		parser.add_argument('test', nargs='?', default=None, 
						help='Test to run (whatsapp, notifications, email, all)')
		
		args = parser.parse_args()
		
		print("\\n==================================================")
		print("            Gmail App Test Launcher               ")
		print("==================================================\\n")
		
		if args.test:
			print(f"Running test: {args.test}\\n")
			success = run_test(args.test)
		else:
			print("No test specified. Running configuration check.\\n")
			success = run_test()
			
			if success:
				print("\\nWhich test would you like to run?")
				print("1. WhatsApp Test")
				print("2. Notifications Test")
				print("3. Email Check Test")
				print("4. All Tests")
				print("5. Exit")
				
				choice = input("\\nEnter your choice (1-5): ").strip()
				
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
		
		print("\\n==================================================")
		print(f"Test result: {'✅ PASS' if success else '❌ FAIL'}")
		print("==================================================")

	if __name__ == "__main__":
		main()
	"""
    
    try:
        with open(filepath, 'w') as file:
            file.write(content)
        os.chmod(filepath, 0o755)  # Make executable
        print(f"✅ Created {filepath}")
    except Exception as e:
        print(f"❌ Error creating {filepath}: {e}")

def main():
    print("\n==================================================")
    print("                Applying Fixes                    ")
    print("==================================================\n")
    
    fix_email_parser()
    fix_notification_service()
    fix_notification_test()
    fix_test_all()
    create_test_launcher()
    
    print("\n==================================================")
    print("              Fixes Complete                     ")
    print("==================================================\n")
    print("You can now run the tests with:")
    print("  python test.py [test_name]")
    print("Where [test_name] can be:")
    print("  - whatsapp:     Test WhatsApp functionality")
    print("  - notifications: Test notification service")
    print("  - email_checks:  Test email checking")
    print("  - all:          Run all tests")
    print("Or run without arguments to check configuration:")
    print("  python test.py\n")

if __name__ == "__main__":
    main()