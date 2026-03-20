# AI Cyberbullying Social App - Backend (Django)

![Django](https://img.shields.io/badge/django-%23092e20.svg?style=for-the-badge&logo=django&logoColor=white)
![DjangoREST](https://img.shields.io/badge/DJANGO-REST-ff1709?style=for-the-badge&logo=django&logoColor=white)
![TensorFlow](https://img.shields.io/badge/TensorFlow-%23FF6F00.svg?style=for-the-badge&logo=TensorFlow&logoColor=white)
![JWT](https://img.shields.io/badge/JWT-black?style=for-the-badge&logo=JSON%20web%20tokens)
![SQLite](https://img.shields.io/badge/sqlite-%2307405e.svg?style=for-the-badge&logo=sqlite&logoColor=white)

A powerful, AI-driven backend for a social media platform designed to proactively detect and mitigate cyberbullying. This project integrates Machine Learning models for real-time text and image analysis within a full-featured social networking API.

## 🔗 Connected Repositories
- **Frontend (Web UI)**: [AI-CyberBulling-Social-App-Web-UI](https://github.com/Rilan-Dev/AI-CyberBulling-Social-App-Web-UI.git)

## 🚀 Features

- **🛡️ AI-Powered Detection**: Real-time analysis of text and images for cyberbullying content using TensorFlow/Keras models.
- **🔐 Secure Authentication**: Robust JWT-based authentication system using `djangorestframework-simplejwt`.
- **👤 User Management**: Comprehensive user profiles, including bio, profile pictures, and follower/following system.
- **📝 Social Networking**: Full CRUD operations for posts and comments with built-in moderation flags.
- **📊 Automated Moderation**: Content is automatically flagged or blocked based on AI confidence scores and analysis results.
- **📖 Interactive API Docs**: Fully documented endpoints with Swagger and ReDoc integration.
- **🧪 Testing Suite**: Built-in test cases for serializers, views, and ML integration.

## 📸 Key Features Showcase

### 🛡️ AI Analysis Engine
Real-time processing of user-generated content to ensure platform safety.
![AI Analysis Engine](docs/screenshots/ai_analysis.svg)

### 📊 Moderation Dashboard
Automated flagging and blocking of harmful content based on confidence scores.
![Moderation Dashboard](docs/screenshots/moderation_dashboard.svg)

## 🛠️ Technical Stack

- **Framework**: Django 4.2.7 & Django REST Framework 3.14.0
- **AI/ML**: TensorFlow, Scikit-learn, NumPy, Pandas
- **Auth**: SimpleJWT (JSON Web Tokens)
- **Database**: SQLite (Development) / PostgreSQL (Production ready)
- **Documentation**: drf-yasg (Swagger/OpenAPI)
- **Image Processing**: Pillow (PIL)

## 📂 Project Structure

```
AI-CyberBulling-Social-App-Backend-Django/
├── project/                # Project configuration (settings, urls, asgi, wsgi)
├── cyberbullying/          # Main application logic
│   ├── models.py           # Database schemas (Post, Comment, UserProfile, etc.)
│   ├── views.py            # API ViewSets and logic
│   ├── ml_views.py         # AI analysis specific endpoints
│   ├── serializers.py      # DRF Serializers for data validation
│   └── tests/              # Unit and integration tests
├── media/                  # Uploaded and analyzed media files
├── requirements.txt        # Python dependencies
└── manage.py               # Django management script
```

## 📥 Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/Rilan-Dev/AI-CyberBulling-Social-App-Backend-Django.git
   cd AI-CyberBulling-Social-App-Backend-Django
   ```

2. **Set up virtual environment**:
   ```bash
   python -m venv venv
   # Windows:
   .\venv\Scripts\activate
   # Linux/macOS:
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run Migrations**:
   ```bash
   python manage.py migrate
   ```

5. **Create Superuser** (optional):
   ```bash
   python manage.py createsuperuser
   ```

6. **Start the server**:
   ```bash
   python manage.py runserver
   ```

## 🔌 API Documentation

Once the server is running, you can access the interactive documentation at:
- **Swagger UI**: `http://localhost:8000/swagger/`
- **ReDoc**: `http://localhost:8000/redoc/`

### Key Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/token/` | POST | Obtain JWT access/refresh tokens |
| `/api/users/register/` | POST | Register a new user |
| `/api/posts/` | GET/POST | List/Create social media posts |
| `/api/analyze-text/` | POST | Analyze raw text for cyberbullying |
| `/api/analyze-image/` | POST | Analyze an image for harmful content |

## 🧪 Testing

Run the test suite to ensure everything is working correctly:
```bash
python manage.py test cyberbullying
```

## 🤝 Contribution

Contributions are welcome! Please follow these steps:
1. Fork the project.
2. Create your feature branch (`git checkout -b feature/AmazingFeature`).
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`).
4. Push to the branch (`git push origin feature/AmazingFeature`).
5. Open a Pull Request.

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.

---
*Developed as part of the AI Cyberbullying Prevention Initiative.*
