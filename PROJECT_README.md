# Intelligent Student Risk Monitoring & Decision Support System

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-2.3+-green.svg)](https://flask.palletsprojects.com/)
[![SQLite](https://img.shields.io/badge/SQLite-3.x-blue.svg)](https://www.sqlite.org/)
[![MySQL](https://img.shields.io/badge/MySQL-8.0+-orange.svg)](https://www.mysql.com/) (Optional)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 📋 Project Description

The **Intelligent Student Risk Monitoring & Decision Support System** is a comprehensive web-based application designed to proactively identify students at risk of academic failure, dropout, or other adverse outcomes. Leveraging machine learning algorithms and data analytics, the system provides early warning alerts to educators, enabling timely interventions and support.

This system integrates multiple data sources including academic performance, attendance records, fee payment status, library usage, and complaint history to generate accurate risk predictions and actionable insights for educational institutions.

## ✨ Features Overview

### Core Features
- **Student Risk Prediction**: ML-powered prediction of student dropout and academic failure risk
- **Early Warning System**: Automated alerts for at-risk students with severity levels
- **Multi-Role Dashboards**: Customized interfaces for administrators, teachers, and students
- **Real-time Analytics**: Interactive charts and reports for data-driven decision making
- **Comprehensive Student Profiles**: 360-degree view of student performance and behavior

### Academic Management
- **Attendance Tracking**: Mark and monitor student attendance with bulk operations
- **Marks Management**: Record and analyze academic performance across subjects
- **Academic Reports**: Generate detailed performance reports and trend analysis

### Administrative Features
- **User Management**: Role-based access control (Admin, Teacher, Student)
- **Fee Management**: Track fee payments, pending dues, and payment history
- **Library Management**: Book inventory, issue/return tracking, and usage analytics
- **Complaint System**: Student complaint submission and resolution tracking

### Machine Learning Capabilities
- **Multiple ML Models**: Random Forest, Gradient Boosting, Logistic Regression, SVM
- **Feature Engineering**: Automated feature extraction from student data
- **Model Training**: Train and evaluate models with custom datasets
- **Prediction Dashboard**: Visual representation of risk scores and factors
- **Model Performance Metrics**: Accuracy, precision, recall, F1-score tracking

### Reporting & Analytics
- **Academic Performance Reports**: Subject-wise and overall performance analysis
- **Attendance Reports**: Attendance trends and patterns
- **Financial Reports**: Fee collection and pending dues analysis
- **Risk Analysis Reports**: Detailed risk factor breakdown

## 🛠️ Tech Stack

### Backend
- **Framework**: Flask 2.3+ (Python)
- **Database**: SQLite 3.x (default), MySQL 8.0+ (optional)
- **ORM**: SQLAlchemy
- **Authentication**: Flask-Login, Flask-WTF
- **ML Framework**: Scikit-learn, Pandas, NumPy

### Frontend
- **Template Engine**: Jinja2
- **CSS Framework**: Bootstrap 5
- **JavaScript**: Vanilla JS with Chart.js for visualizations
- **Icons**: Font Awesome

### DevOps & Deployment
- **Containerization**: Docker, Docker Compose
- **Web Server**: Nginx (production)
- **WSGI Server**: Gunicorn
- **Version Control**: Git

### Data Science
- **Data Processing**: Pandas, NumPy
- **Machine Learning**: Scikit-learn
- **Visualization**: Matplotlib, Seaborn
- **Model Persistence**: Joblib

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Client Layer                              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │   Admin UI  │  │ Teacher UI  │  │ Student UI  │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                  Application Layer                           │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              Flask Application                       │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐ │   │
│  │  │   Routes    │  │   Forms     │  │   Models    │ │   │
│  │  └─────────────┘  └─────────────┘  └─────────────┘ │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐ │   │
│  │  │   ML Engine │  │  Utilities  │  │  Templates  │ │   │
│  │  └─────────────┘  └─────────────┘  └─────────────┘ │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    Data Layer                                │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │   SQLite DB  │  │  ML Models  │  │  Static     │         │
│  │  (default)   │  │  (.pkl)     │  │  Files      │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
└─────────────────────────────────────────────────────────────┘
```

### Component Overview

1. **Routes Layer**: Handles HTTP requests and business logic
   - `auth.py`: Authentication and authorization
   - `admin.py`: Administrative operations
   - `student.py`: Student-specific operations
   - `main.py`: General routes and landing pages

2. **Models Layer**: Database models and data access
   - User, Student, Subject, Attendance, Marks
   - Fee, Library, Complaint, Prediction, Alert, ActivityLog

3. **ML Engine**: Machine learning pipeline
   - `predictor.py`: Real-time predictions
   - `trainer.py`: Model training and evaluation
   - `feature_engineering.py`: Feature extraction
   - `early_warning.py`: Alert generation

4. **Forms Layer**: Input validation and CSRF protection
   - Authentication forms
   - Student management forms
   - Academic forms (attendance, marks)
   - Administrative forms

## 📦 Installation Instructions

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- Git
- (Optional) MySQL 8.0+ if you prefer MySQL over SQLite

### Quick Start

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd student-risk-monitoring
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application** (database is created automatically)
   ```bash
   python main.py
   ```

5. **Seed sample data** (optional, but recommended)
   ```bash
   python seed_data.py
   ```

6. **Access the application**
   - Open browser and navigate to `http://localhost:5000`

### Default Login Credentials
| Role | Username | Password |
|------|----------|----------|
| Admin | admin | admin123 |
| Teacher | teacher1 | teacher123 |
| Student | STU001 | student123 |

> **Note**: The `.env` file is pre-configured for SQLite. The database file (`instance/student_risk.db`) will be created automatically when you first run the application. For MySQL support, see the detailed installation guide.

## 📘 Usage Guide

### For Administrators
1. **Dashboard**: View overall statistics and at-risk students
2. **User Management**: Create and manage teacher/student accounts
3. **ML Models**: Train new models and view prediction accuracy
4. **Alerts**: Monitor and manage early warning alerts
5. **Reports**: Generate comprehensive academic and financial reports

### For Teachers
1. **Dashboard**: View class-specific statistics
2. **Attendance**: Mark and track student attendance
3. **Marks**: Record and analyze student performance
4. **Students**: View student profiles and risk assessments

### For Students
1. **Dashboard**: View personal academic summary
2. **Attendance**: Check attendance records
3. **Marks**: View grades and performance trends
4. **Fees**: Check fee payment status
5. **Library**: View issued books and history
6. **Complaints**: Submit and track complaints

## 📚 API Documentation

Comprehensive API documentation is available in [`docs/API_DOCUMENTATION.md`](docs/API_DOCUMENTATION.md).

### Key Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/students` | GET | List all students |
| `/api/students/<id>` | GET | Get student details |
| `/api/predictions/<student_id>` | GET | Get risk prediction |
| `/api/alerts` | GET | List all alerts |
| `/api/reports/academic` | GET | Generate academic report |

## 📸 Screenshots

### Admin Dashboard
![Admin Dashboard](docs/screenshots/admin_dashboard.png)

### Student Risk Prediction
![Risk Prediction](docs/screenshots/risk_prediction.png)

### Attendance Tracking
![Attendance](docs/screenshots/attendance.png)

### ML Model Training
![Model Training](docs/screenshots/model_training.png)

*Note: Screenshots are placeholders. Add actual screenshots to `docs/screenshots/` directory.*

## 🤝 Contributing

We welcome contributions to improve the Student Risk Monitoring System! Please follow these guidelines:

### How to Contribute

1. **Fork the repository**
2. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. **Make your changes**
4. **Write/update tests**
5. **Commit your changes**
   ```bash
   git commit -m "Add: description of your changes"
   ```
6. **Push to your branch**
   ```bash
   git push origin feature/your-feature-name
   ```
7. **Create a Pull Request**

### Code Style Guidelines
- Follow PEP 8 for Python code
- Use meaningful variable and function names
- Add docstrings to all functions and classes
- Write unit tests for new features
- Update documentation for any API changes

### Reporting Issues
- Use the GitHub Issues tab
- Provide detailed description of the issue
- Include steps to reproduce
- Attach relevant logs or screenshots

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

```
MIT License

Copyright (c) 2024 Student Risk Monitoring System

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## 📞 Contact Information

**Project Maintainer**: [Your Name]
**Email**: [your.email@example.com]
**GitHub**: [https://github.com/yourusername]
**LinkedIn**: [https://linkedin.com/in/yourprofile]

### Support
- **Issues**: [GitHub Issues](https://github.com/yourusername/student-risk-monitoring/issues)
- **Documentation**: [Project Wiki](https://github.com/yourusername/student-risk-monitoring/wiki)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/student-risk-monitoring/discussions)

## 🙏 Acknowledgments

- Flask community for the excellent web framework
- Scikit-learn team for machine learning tools
- Bootstrap team for the responsive CSS framework
- Chart.js for beautiful visualizations
- All contributors who have helped improve this project

---

**Made with ❤️ for educational institutions worldwide**
