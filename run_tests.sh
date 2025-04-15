#!/bin/bash
echo "Running Cyberbullying API Tests"
echo "=============================="

echo "Checking if test image exists..."
if [ ! -f "test-image.jpg" ]; then
    echo "Creating test image..."
    python -c "from PIL import Image; img = Image.new('RGB', (100, 100), color='red'); img.save('test-image.jpg')"
    if [ $? -ne 0 ]; then
        echo "Failed to create test image."
        exit 1
    fi
    echo "Test image created."
else
    echo "Test image already exists."
fi

echo "Checking if Django server is running..."
python -c "import requests; response = requests.get('http://localhost:8000/admin/'); print('Django server is running.' if response.status_code in [200, 302] else 'Django server is not running.')"
if [ $? -ne 0 ]; then
    echo "Failed to check if Django server is running."
    echo "Please make sure the Django server is running with: python manage.py runserver"
    exit 1
fi

echo "Running Newman tests..."
npm exec -- newman run postman_collection.json -e postman_environment.json
if [ $? -ne 0 ]; then
    echo "Tests failed."
    exit 1
fi

echo "Tests completed successfully."
