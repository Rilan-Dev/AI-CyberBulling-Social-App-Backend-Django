@echo off
echo Running Cyberbullying API Tests
echo ==============================

echo Checking if test image exists...
if not exist test-image.jpg (
    echo Creating test image...
    python -c "from PIL import Image; img = Image.new('RGB', (100, 100), color='red'); img.save('test-image.jpg')"
    if %errorlevel% neq 0 (
        echo Failed to create test image.
        exit /b 1
    )
    echo Test image created.
) else (
    echo Test image already exists.
)

echo Checking if Django server is running...
python -c "import requests; response = requests.get('http://localhost:8000/admin/'); print('Django server is running.' if response.status_code in [200, 302] else 'Django server is not running.')"
if %errorlevel% neq 0 (
    echo Failed to check if Django server is running.
    echo Please make sure the Django server is running with: python manage.py runserver
    exit /b 1
)

echo Running Newman tests...
call npm exec -- newman run postman_collection.json -e postman_environment.json
if %errorlevel% neq 0 (
    echo Tests failed.
    exit /b 1
)

echo Tests completed successfully.
