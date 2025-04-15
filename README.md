# Cyberbullying Prediction API

This is a Django REST Framework API for a cyberbullying prediction system with social media features.

## Features

- User authentication with JWT tokens
- User profiles
- Posts and comments with cyberbullying detection
- Text and image analysis for cyberbullying content
- API documentation with Swagger and ReDoc

## Setup

### Prerequisites

- Python 3.8+
- pip
- virtualenv (optional)
- Node.js and npm (for running Postman tests with Newman)

### Installation

1. Clone the repository:
   \`\`\`
   git clone https://github.com/yourusername/cyberbullying-prediction-api.git
   cd cyberbullying-prediction-api
   \`\`\`

2. Create and activate a virtual environment (optional):
   \`\`\`
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   \`\`\`

3. Install dependencies:
   \`\`\`
   pip install -r requirements.txt
   \`\`\`

4. Apply migrations:
   \`\`\`
   python manage.py migrate
   \`\`\`

5. Create a superuser:
   \`\`\`
   python manage.py createsuperuser
   \`\`\`

6. Run the development server:
   \`\`\`
   python manage.py runserver
   \`\`\`

The API will be available at http://localhost:8000/api/

## API Documentation

- Swagger UI: http://localhost:8000/swagger/
- ReDoc: http://localhost:8000/redoc/

## API Endpoints

### Authentication

- `POST /api/token` - Get JWT token
- `POST /api/token/refresh` - Refresh JWT token
- `POST /api/token/verify` - Verify JWT token
- `POST /api/users/register` - Register a new user
- `GET /api/users/me` - Get current user information

### Posts

- `GET /api/posts` - List all posts
- `POST /api/posts` - Create a new post
- `GET /api/posts/{id}` - Get a specific post
- `PUT /api/posts/{id}` - Update a post
- `DELETE /api/posts/{id}` - Delete a post
- `POST /api/posts/{id}/like` - Like or unlike a post

### Comments

- `GET /api/comments` - List all comments
- `POST /api/comments` - Create a new comment
- `GET /api/comments/{id}` - Get a specific comment
- `PUT /api/comments/{id}` - Update a comment
- `DELETE /api/comments/{id}` - Delete a comment

### Analysis

- `POST /api/analyze-text` - Analyze text for cyberbullying content
- `POST /api/analyze-image` - Analyze image for cyberbullying content

## Testing with Postman

### Prerequisites for Testing

- **Node.js and npm**: Required to run Newman (Postman CLI)
  - Download from: https://nodejs.org/
  - After installation, you should be able to run `node -v` and `npm -v` to verify

- **Newman**: Postman's command-line collection runner
  - We'll use `npm exec -- newman` to run it without installing globally

### Running Tests

#### Option 1: Using the Provided Scripts (Recommended)

We provide several scripts to make testing easier:

**For Windows users:**
\`\`\`
run_tests.bat
\`\`\`

**For Unix/Linux/Mac users:**
\`\`\`
./run_tests.sh
\`\`\`

**Using Python (cross-platform):**
\`\`\`
python run_tests.py
\`\`\`

These scripts will:
1. Create a test image if it doesn't exist
2. Check if the Django server is running and start it if needed
3. Run the Postman tests using Newman

#### Option 2: Manual Testing

1. Make sure the Django server is running:
   \`\`\`
   python manage.py runserver
   \`\`\`

2. Make sure the test image exists in the backend directory:
   \`\`\`
   # The script can create it for you
   python -c "from PIL import Image; img = Image.new('RGB', (100, 100), color='red'); img.save('test-image.jpg')"
   \`\`\`

3. Run the tests with Newman:
   \`\`\`
   npm exec -- newman run postman_collection.json -e postman_environment.json
   \`\`\`

#### Option 3: Using Postman Desktop App

1. Import the collection from `postman_collection.json`
2. Import the environment from `postman_environment.json`
3. Make sure the test image exists in the backend directory
4. Run the collection from the Postman app

## Troubleshooting

If you encounter issues with the Postman tests:

1. **401 Unauthorized for Register**: Make sure the RegisterView has `permission_classes = [AllowAny]` and that the global permission class in settings.py is set to `'rest_framework.permissions.AllowAny'`

2. **Image analysis fails**: Ensure the test image file is in the backend directory. You can create it with:
   ```python
   from PIL import Image
   img = Image.new('RGB', (100, 100), color='red')
   img.save('test-image.jpg')
   \`\`\`

3. **Token refresh fails**: Make sure you've obtained a valid token first by running the "Get Token" request

4. **Newman command not found**: Make sure Node.js and npm are installed. Try using:
   \`\`\`
   npm exec -- newman run postman_collection.json -e postman_environment.json
   \`\`\`
   instead of using npx directly.

5. **Windows-specific issues**: If you're on Windows and having trouble with the Python script, try using the batch file:
   \`\`\`
   run_tests.bat
   \`\`\`

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Acknowledgements

- Django REST Framework
- Simple JWT
- TensorFlow and scikit-learn for ML models
- Postman for API testing
