#!/usr/bin/env python
import os
import sys
import subprocess
import time
import shutil
from PIL import Image

def create_test_image():
    """Create a simple test image if it doesn't exist"""
    if not os.path.exists('test-image.jpg'):
        print("Creating test image...")
        # Create a simple 100x100 red image
        img = Image.new('RGB', (100, 100), color='red')
        img.save('test-image.jpg')
        print("Test image created.")
    else:
        print("Test image already exists.")

def check_node_installed():
    """Check if Node.js and npm are installed"""
    node_installed = shutil.which('node') is not None
    npm_installed = shutil.which('npm') is not None
    
    if not (node_installed and npm_installed):
        print("\nERROR: Node.js and npm are required to run the Postman tests.")
        print("Please install Node.js from https://nodejs.org/")
        print("\nAfter installation, you can run the tests manually with:")
        print("npm exec -- newman run postman_collection.json -e postman_environment.json")
        return False
    
    return True

def run_tests_manually():
    """Provide instructions for running tests manually"""
    print("\nTo run the tests manually:")
    print("1. Make sure the Django server is running:")
    print("   python manage.py runserver")
    print("\n2. In a separate terminal, run the Postman tests:")
    print("   npm exec -- newman run postman_collection.json -e postman_environment.json")
    print("\nOr you can use the provided batch file:")
    print("   run_tests.bat")
    print("\nOr if you prefer, you can use Postman desktop app:")
    print("1. Import the collection from postman_collection.json")
    print("2. Import the environment from postman_environment.json")
    print("3. Run the collection from the Postman app")

def run_tests():
    """Run the Postman tests using Newman"""
    print("Running Postman tests...")
    try:
        # Make sure the Django server is running
        print("Checking if Django server is running...")
        try:
            import requests
            response = requests.get('http://localhost:8000/admin/')
            if response.status_code == 200 or response.status_code == 302:
                print("Django server is running.")
            else:
                print("Django server returned unexpected status code:", response.status_code)
                start_django_server()
        except requests.exceptions.ConnectionError:
            print("Django server is not running.")
            start_django_server()
        except ImportError:
            print("WARNING: requests package not installed. Cannot check if Django server is running.")
            print("Please make sure the Django server is running with: python manage.py runserver")
        
        # Check if Node.js is installed
        if not check_node_installed():
            run_tests_manually()
            return
        
        # Run the tests using npm directly
        print("\nRunning Newman tests...")
        try:
            # On Windows, we need to use shell=True to run npm commands
            if os.name == 'nt':  # Windows
                subprocess.run('npm exec -- newman run postman_collection.json -e postman_environment.json', 
                               shell=True, check=True)
            else:  # Unix/Linux/Mac
                subprocess.run(['npm', 'exec', '--', 'newman', 'run', 'postman_collection.json', 
                                '-e', 'postman_environment.json'], check=True)
            print("\nTests completed successfully.")
        except subprocess.CalledProcessError as e:
            print(f"\nError running tests: {e}")
            run_tests_manually()
        except FileNotFoundError:
            print(f"\nError: Command 'npm' not found.")
            run_tests_manually()
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        run_tests_manually()

def start_django_server():
    """Start the Django development server"""
    print("Starting Django server...")
    try:
        # Start the server in a new process
        if os.name == 'nt':  # Windows
            subprocess.Popen([sys.executable, 'manage.py', 'runserver'], 
                             creationflags=subprocess.CREATE_NEW_CONSOLE)
        else:  # Unix/Linux/Mac
            subprocess.Popen([sys.executable, 'manage.py', 'runserver'])
        # Wait for the server to start
        print("Waiting for Django server to start...")
        time.sleep(5)
        print("Django server should be running now.")
    except Exception as e:
        print(f"Error starting Django server: {e}")
        sys.exit(1)

if __name__ == '__main__':
    # Make sure we're in the backend directory
    if not os.path.exists('manage.py'):
        print("Error: This script must be run from the backend directory.")
        sys.exit(1)
    
    # Create the test image
    create_test_image()
    
    # Run the tests
    run_tests()
