# Cyberbullying Prediction API Documentation and Testing

This directory contains comprehensive documentation and testing resources for the Cyberbullying Prediction API.

## Documentation

The API documentation is available in the following formats:

- **Markdown**: See `api_documentation.md` for a detailed description of all endpoints, request/response formats, and examples.
- **Swagger UI**: Available at `http://localhost:8000/swagger/` when the server is running.
- **ReDoc**: Available at `http://localhost:8000/redoc/` when the server is running.

## Testing

### Automated Tests

The API includes comprehensive automated tests for models, serializers, and views. To run the tests:

1. Navigate to the backend directory:
   \`\`\`
   cd backend
   \`\`\`

2. Run the test script:
   \`\`\`
   python run_api_tests.py
   \`\`\`

   This will:
   - Create a test image if it doesn't exist
   - Run all the tests in the `cyberbullying.tests` package
   - Display the test results

### Manual Testing with Postman

For manual testing, we provide a Postman collection and environment:

1. Import the collection from `postman/cyberbullying_api_collection.json`
2. Import the environment from `postman/cyberbullying_api_environment.json`
3. Set the `base_url` variable in the environment if needed (default is `http://localhost:8000`)
4. Run the collection

#### Key Test Flows

1. **Authentication Flow**:
   - Register a new user
   - Get a token
   - Refresh the token
   - Verify the token
   - Get the current user profile

2. **Post Flow**:
   - Create a post
   - List posts
   - Get a specific post
   - Update a post
   - Like/unlike a post
   - Delete a post

3. **Comment Flow**:
   - Create a comment
   - List comments
   - Get a specific comment
   - Update a comment
   - Delete a comment

4. **Analysis Flow**:
   - Analyze text
   - Analyze image

## API Response Examples

### Text Analysis Response

\`\`\`json
{
  "success": true,
  "status": "clean",
  "prediction": "not_cyberbullying",
  "confidence": 0.95,
  "reason": null,
  "processed_text": "this is a sample text for analysis"
}
\`\`\`

### Image Analysis Response

\`\`\`json
{
  "success": true,
  "prediction": "Non_Offensive",
  "status": "clean",
  "confidence": 0.95,
  "reason": null,
  "filename": "image.jpg"
}
\`\`\`

### Post Response with Analysis Reports

\`\`\`json
{
  "id": 1,
  "user": {
    "id": 1,
    "username": "testuser",
    "email": "test@example.com",
    "first_name": "Test",
    "last_name": "User"
  },
  "content": "This is a sample post",
  "image": "http://example.com/media/post_images/image.jpg",
  "status": "clean",
  "reason": null,
  "confidence": 0.95,
  "like_count": 0,
  "is_liked": false,
  "comments": [],
  "created_at": "2023-01-01T12:00:00Z",
  "text_analysis": {
    "success": true,
    "prediction": "not_cyberbullying",
    "status": "clean",
    "confidence": 0.95,
    "reason": null,
    "processed_text": "this is a sample post"
  },
  "image_analysis": {
    "success": true,
    "prediction": "Non_Offensive",
    "status": "clean",
    "confidence": 0.95,
    "reason": null,
    "filename": "image.jpg"
  }
}
\`\`\`

## Troubleshooting

If you encounter any issues with the API or tests, please check the following:

1. Make sure the Django server is running
2. Verify that the database migrations have been applied
3. Check that the test image exists in the backend directory
4. Ensure that the JWT token is valid and not expired
5. Check the server logs for any error messages

For more information, please refer to the main README file in the project root directory.
