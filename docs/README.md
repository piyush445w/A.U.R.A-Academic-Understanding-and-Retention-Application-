# A.U.R.A - Academic Understanding and Retention Application

## Project Overview

The A.U.R.A - Academic Understanding and Retention Application is a comprehensive web application designed to help educational institutions identify and support students at risk of academic failure or dropout. The system leverages machine learning algorithms to analyze various student data points including attendance, academic performance, fee payments, and other behavioral indicators to generate early warning alerts and provide actionable insights for educators and administrators.

## Features

- **Student Risk Prediction**: Machine learning models analyze student data to predict dropout risk levels (Low, Medium, High)
- **Early Warning System**: Automated alerts for attendance issues, academic performance decline, fee defaults, and behavioral concerns
- **Multi-role Access Control**: Role-based access for administrators, teachers, and students
- **Comprehensive Dashboard**: Visual analytics and reports for monitoring student performance and risk trends
- **Academic Tracking**: Attendance management, grade recording, and subject management
- **Financial Management**: Fee tracking, payment processing, and overdue notifications
- **Library Management**: Book inventory, issue/return tracking, and fine management
- **Complaint Handling**: Student grievance redressal system with tracking and resolution workflow
- **Data Export & Reporting**: Generate reports in various formats for administrative decision-making
- **Secure Authentication**: Secure login system with password hashing and session management

## Technology Stack

### Backend
- **Framework**: Flask 3.0.0 (Python web framework)
- **Database**: MySQL 8.0+ with SQLAlchemy ORM
- **Authentication**: Flask-Login for user session management
- **Form Handling**: Flask-WTF for secure form processing
- **Environment**: Python-dotenv for configuration management

### Machine Learning
- **ML Library**: Scikit-learn 1.3.2 for predictive modeling
- **Data Processing**: Pandas 2.1.4 and NumPy 1.26.2 for data manipulation
- **Model Persistence**: Joblib 1.3.2 for model serialization
- **Features**: Random Forest algorithm for risk prediction

### Frontend
- **Templating**: Jinja2 for HTML templating
- **Styling**: CSS3 with responsive design
- **JavaScript**: Vanilla JS with Chart.js for data visualization
- **Bootstrap**: Responsive UI components (implicit in templates)

### Development Tools
- **Version Control**: Git
- **IDE**: VS Code (or any Python-compatible IDE)
- **Testing**: Built-in Flask testing capabilities
- **Deployment**: WSGI-compatible servers (Gunicorn, uWSGI)

## System Architecture

The system follows a Model-View-Controller (MVC) architecture:
- **Models**: Database entities defined in `app/models/`
- **Views**: HTML templates in `app/templates/`
- **Controllers**: Route handlers in `app/routes/`
- **Services**: ML prediction and business logic in `app/ml/`
- **Utilities**: Helper functions and decorators in `app/utils/`

## Setup Instructions

### Prerequisites
- Python 3.8+
- MySQL Server 8.0+
- pip (Python package manager)
- Git (for version control)

### Installation Steps

1. **Clone the Repository**
   ```bash
   git clone <repository-url>
   cd intelligent-student-risk-monitoring
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv venv
   # On Windows
   venv\Scripts\activate
   # On Unix/Linux/MacOS
   source venv/bin/activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Environment**
   ```bash
   cp .env.example .env
   # Edit .env file with your configuration:
   # - SECRET_KEY: Secret key for Flask sessions
   # - DATABASE_URL: MySQL connection string
   # - MAIL_*: Email configuration for notifications
   ```

5. **Setup Database**
   ```bash
   # Ensure MySQL server is running
   # Create database (will be created automatically on first run)
   # Or manually create:
   # CREATE DATABASE student_risk_monitoring;
   ```

6. **Initialize Application**
   ```bash
   python main.py
   # Or for development:
   # flask run --host=0.0.0.0 --port=5000
   ```

7. **Access the Application**
   Open your web browser and navigate to: `http://localhost:5000`

### Default Login Credentials
After initial setup, you can log in with:
- **Admin**: username: `admin`, password: `admin123` (change after first login)
- **Teacher**: username: `teacher1`, password: `teacher123` (change after first login)
- **Student**: username: `student1`, password: `student123` (change after first login)

## Project Structure

```
intelligent-student-risk-monitoring/
├── app/
│   ├── __init__.py
│   ├── models/           # Database models
│   ├── routes/           # Application routes (controllers)
│   ├── ml/               # Machine learning components
│   ├── forms/            # WTForms definitions
│   ├── static/           # CSS, JavaScript, images
│   ├── templates/        # HTML templates
│   └── utils/            # Utility functions
├── database/             # Database schema and migrations
├── datasets/             # Sample datasets for training
├── docs/                 # Documentation files
├── models/               # Trained ML models
├── notebooks/            # Jupyter notebooks for ML experimentation
├── requirements.txt      # Python dependencies
├── config.py             # Application configuration
├── main.py               # Application entry point
└── .env.example          # Environment variables template
```

## API Endpoints

The system provides RESTful API endpoints for integration with other systems. Detailed API documentation is available in `docs/API_DOCUMENTATION.md`.

## Machine Learning Model

The system uses a Random Forest classifier trained on historical student data to predict dropout risk. The model considers features such as:
- Attendance percentage
- Average academic marks
- Fee payment status
- Library transaction history
- Complaint frequency
- Demographic information

Model performance metrics:
- Accuracy: 87.50%
- Precision: 86.00%
- Recall: 89.00%
- F1-Score: 87.48%

## Configuration

Key configuration options in `config.py`:
- `SECRET_KEY`: Flask session security key
- `SQLALCHEMY_DATABASE_URI`: Database connection string
- `HIGH_RISK_THRESHOLD`: Risk score threshold for high-risk classification (0.7)
- `MEDIUM_RISK_THRESHOLD`: Risk score threshold for medium-risk classification (0.4)
- `LOW_RISK_THRESHOLD`: Risk score threshold for low-risk classification (0.2)
- `MAIL_*`: Email server settings for notifications

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contact

For questions or support, please contact the development team at: support@studentrisksystem.edu

## Acknowledgments

- Open source community for Flask and related libraries
- Educational institutions for providing domain expertise and requirements
- Machine learning researchers for predictive modeling techniques