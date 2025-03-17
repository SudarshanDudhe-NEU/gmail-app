#!/usr/bin/env python

import os
import sys

def fix_notification_service():
    """Fix the imports in notification_service.py"""
    filepath = "services/notification_service.py"
    print(f"Fixing {filepath}...")
    
    try:
        with open(filepath, 'r') as file:
            content = file.read()
        
        # First check if the correct imports are already there
        if 'from utils.email_parser import extract_job_title' in content:
            print(f"✅ Notification service already fixed")
            return True
            
        # Replace the import statement with the correct ones
        if 'from utils.email_parser import extract_job_details' in content:
            content = content.replace(
                'from utils.email_parser import extract_job_details',
                'from utils.email_parser import extract_job_title, extract_company, extract_location, extract_salary'
            )
            
            # Make sure we're using the imported functions
            if 'job_details = extract_job_details(body)' in content:
                content = content.replace(
                    'job_details = extract_job_details(body)',
                    'job_title = extract_job_title(body)\n        company = extract_company(body)\n        location = extract_location(body)\n        salary = extract_salary(body)'
                )
                
            # Fix the formatting part to use the new variables
            if 'if job_details:' in content:
                content = content.replace(
                    'if job_details:',
                    'if job_title:'
                )
                content = content.replace(
                    'message += f"*Job Details:* {job_details}\\n"',
                    'message += f"*Position:* {job_title}\\n"'
                )
                
            # Add the rest of the job details
            job_details_added = False
            if 'message += f"*Position:* {job_title}\\n"' in content and 'message += f"*Company:* {company}\\n"' not in content:
                position_line = 'message += f"*Position:* {job_title}\\n"'
                company_block = (
                    'message += f"*Position:* {job_title}\\n"\n'
                    '        if company:\n'
                    '            message += f"*Company:* {company}\\n"\n'
                    '        if location:\n'
                    '            message += f"*Location:* {location}\\n"\n'
                    '        if salary:\n'
                    '            message += f"*Salary:* {salary}\\n"'
                )
                content = content.replace(position_line, company_block)
                job_details_added = True
                
            with open(filepath, 'w') as file:
                file.write(content)
                
            print(f"✅ Updated imports in {filepath}")
            if job_details_added:
                print(f"✅ Added job details formatting in {filepath}")
                
            return True
        else:
            print(f"⚠️ Could not find import statement to replace in {filepath}")
            return False
    except Exception as e:
        print(f"❌ Error fixing {filepath}: {e}")
        return False

def manually_fix_notification_service():
    """Manually fix the notification service file"""
    filepath = "services/notification_service.py"
    print(f"Manually fixing {filepath}...")
    
    try:
        # Read the current file to get most of the content
        with open(filepath, 'r') as file:
            content = file.read()
            
        # Find key sections to preserve
        import_section = content.split("import logging")[0] + "import logging\n"
        class_def = "class NotificationService:"
        class_section_start = content.find(class_def)
        
        if class_section_start == -1:
            print(f"❌ Could not find NotificationService class in {filepath}")
            return False
        
        # Create the fixed file content
        fixed_content = import_section
        fixed_content += "from utils.email_parser import extract_job_title, extract_company, extract_location, extract_salary\n\n"
        fixed_content += content[class_section_start:content.find("def format_message")]
        
        # Add the fixed format_message method
        format_message = """    def format_message(self, subject, body, sender, received_time):
        \"\"\"Format message for notifications with relevant details\"\"\"
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
        fixed_content += format_message
        
        # Add the rest of the file
        send_notification_start = content.find("def send_notification")
        if send_notification_start != -1:
            fixed_content += content[send_notification_start:]
        
        # Write the fixed file
        with open(filepath, 'w') as file:
            file.write(fixed_content)
            
        print(f"✅ Manually fixed {filepath}")
        return True
    except Exception as e:
        print(f"❌ Error manually fixing {filepath}: {e}")
        return False

def main():
    print("\n==================================================")
    print("          Fixing Notification Service            ")
    print("==================================================\n")
    
    # Try automatic fix first
    auto_fixed = fix_notification_service()
    
    # If automatic fix failed, try manual fix
    if not auto_fixed:
        print("\nAttempting manual fix...")
        manually_fix_notification_service()
    
    print("\n==================================================")
    print("                Fix Complete                     ")
    print("==================================================\n")
    print("You can now run the notification test with:")
    print("  python test.py notifications\n")
    print("Or run all tests with:")
    print("  python test.py all\n")

if __name__ == "__main__":
    main()