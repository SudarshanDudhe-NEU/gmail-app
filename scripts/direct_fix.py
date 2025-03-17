#!/usr/bin/env python

import os
import sys

def completely_fix_notification_service():
    """Completely fix the notification service file by replacing the format_message method"""
    filepath = "services/notification_service.py"
    print(f"Completely fixing {filepath}...")
    
    try:
        with open(filepath, 'r') as file:
            content = file.read()
        
        # Make sure we have the right imports
        if 'from utils.email_parser import extract_job_title' not in content:
            if 'from utils.email_parser import extract_job_details' in content:
                content = content.replace(
                    'from utils.email_parser import extract_job_details',
                    'from utils.email_parser import extract_job_title, extract_company, extract_location, extract_salary'
                )
            else:
                # Add the import if not present
                import_line = 'import logging\n'
                if import_line in content:
                    content = content.replace(
                        import_line, 
                        'import logging\nfrom utils.email_parser import extract_job_title, extract_company, extract_location, extract_salary\n'
                    )
        
        # Find and replace the entire format_message method
        start_pattern = "    def format_message"
        end_pattern = "    def send_notification"
        
        start_index = content.find(start_pattern)
        end_index = content.find(end_pattern, start_index + 1)
        
        if start_index != -1 and end_index != -1:
            # Extract parts before and after the method
            before = content[:start_index]
            after = content[end_index:]
            
            # New format_message method
            new_method = """
            def format_message(self, subject, body, sender, received_time):
				""Format message for notifications with relevant details""
				try:
					# Get timestamp
					received_dt = datetime.fromtimestamp(received_time / 1000)
					time_str = received_dt.strftime("%Y-%m-%d %H:%M:%S")
					
					# Extract job details if available
					job_title = extract_job_title(body)
					company = extract_company(body)
					location = extract_location(body)
					salary = extract_salary(body)
					
					# Build message
					message = f"📨 *New Important Email*\\n\\n"
					message += f"*Subject:* {subject}\\n"
					message += f"*From:* {sender}\\n"
					message += f"*Time:* {time_str}\\n\\n"
					
					# Add job details if available
					if job_title:
						message += f"*Position:* {job_title}\\n"
					if company:
						message += f"*Company:* {company}\\n"
					if location:
						message += f"*Location:* {location}\\n"
					if salary:
						message += f"*Salary:* {salary}\\n"
						
					message += f"\\n{body[:200]}...\\n"
					
					return message
				except Exception as e:
					self.logger.error(f"Error formatting message: {e}")
					return f"New email from {sender}: {subject}"

				"""
            
            # Combine parts
            new_content = before + new_method + after
            
            # Write the fixed file
            with open(filepath, 'w') as file:
                file.write(new_content)
                
            print(f"✅ Completely replaced format_message method in {filepath}")
            return True
        else:
            print(f"⚠️ Could not find format_message method in {filepath}")
            return False
    except Exception as e:
        print(f"❌ Error fixing {filepath}: {e}")
        return False

def main():
    print("\n==================================================")
    print("       Complete Notification Service Fix          ")
    print("==================================================\n")
    
    completely_fix_notification_service()
    
    print("\n==================================================")
    print("                Fix Complete                     ")
    print("==================================================\n")
    print("You can now run the notification test with:")
    print("  python test.py notifications\n")
    print("Or run all tests with:")
    print("  python test.py all\n")

if __name__ == "__main__":
    main()