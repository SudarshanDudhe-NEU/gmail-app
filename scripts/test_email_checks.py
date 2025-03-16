#!/usr/bin/env python
# filepath: /Users/sudarshan/Job and Prep/Projects/gmail-app/test_email_checks.py

import logging
import argparse
from datetime import datetime
import config.settings as settings
from check_old_emails import check_old_emails

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(settings.LOG_FILE),
        logging.StreamHandler()
    ]
)

def run_test(test_name, query, max_results=10):
    """Run a specific email test with the given query"""
    logging.info(f"Running test: {test_name}")
    logging.info(f"Query: {query}")
    logging.info(f"Max results: {max_results}")
    
    try:
        check_old_emails(query, max_results)
        logging.info(f"✅ Test '{test_name}' completed successfully")
    except Exception as e:
        logging.error(f"❌ Test '{test_name}' failed: {e}")

def main():
    """Run email notification tests"""
    parser = argparse.ArgumentParser(description='Test email checking and notifications')
    parser.add_argument('--test', choices=['recent', 'important', 'specific', 'all'], 
                      default='all', help='Which test to run')
    args = parser.parse_args()
    
    logging.info("Starting email check tests...")
    
    # Define test cases
    tests = {
        'recent': {
            'name': 'Recent Emails',
            'query': 'newer_than:3d',  # Emails from the last 3 days
            'max_results': 10
        },
        'important': {
            'name': 'Important Emails',
            'query': 'is:important',  # Emails marked as important by Gmail
            'max_results': 10
        },
        'specific': {
            'name': 'Specific Sender',
            'query': 'from:notifications@github.com',  # Replace with a sender you want to test
            'max_results': 5
        }
    }
    
    if args.test == 'all':
        for test_id, test_config in tests.items():
            run_test(test_config['name'], test_config['query'], test_config['max_results'])
    else:
        test_config = tests[args.test]
        run_test(test_config['name'], test_config['query'], test_config['max_results'])
    
    logging.info("Email check tests complete!")

if __name__ == "__main__":
    main()