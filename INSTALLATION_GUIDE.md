# Installation Guide

## Intelligent Student Risk Monitoring & Decision Support System

This guide provides step-by-step instructions for setting up the Student Risk Monitoring System on your local machine or server.

---

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [MySQL Setup](#mysql-setup)
3. [Python Environment Setup](#python-environment-setup)
4. [Dependencies Installation](#dependencies-installation)
5. [Database Configuration](#database-configuration)
6. [Application Initialization](#application-initialization)
7. [Running the Application](#running-the-application)
8. [Troubleshooting](#troubleshooting)

---

## Prerequisites

Before you begin, ensure you have the following installed on your system:

### Required Software

| Software | Version | Installation |
|----------|---------|--------------|
| Python | 3.8+ | [python.org](https://www.python.org/downloads/) |
| MySQL | 8.0+ | [mysql.com](https://dev.mysql.com/downloads/) |
| pip | Latest | Comes with Python |
| Git | Latest | [git-scm.com](https://git-scm.com/downloads) |

### Optional Software

| Software | Purpose |
|----------|---------|
| Docker | Containerized deployment |
| Docker Compose | Multi-container orchestration |
| Nginx | Production web server |
| Virtualenv | Python environment isolation |

### System Requirements

- **Operating System**: Windows 10+, macOS 10.15+, or Ubuntu 18.04+
- **RAM**: Minimum 4GB (8GB recommended)
- **Storage**: At least 2GB free space
- **Network**: Internet connection for package installation

### Verify Installation

```bash
# Check Python version
python --version
# or
python3 --version

# Check MySQL version
mysql --version

# Check pip version
pip --version

# Check Git version
git --version
```

---

## MySQL Setup

### 1. Install MySQL

#### Windows
1. Download MySQL Installer from [mysql.com](https://dev.mysql.com/downloads/installer/)
2. Run the installer and select "Developer Default"
3. Follow the installation wizard
4. Set a root password (remember this!)
5. Complete the installation

#### macOS
```bash
# Using Homebrew
brew install mysql
brew services start mysql

# Secure installation
mysql_secure_installation
```

#### Ubuntu/Debian
```bash
# Update package list
sudo apt update

# Install MySQL
sudo apt install mysql-server

# Start MySQL service
sudo systemctl start mysql
sudo systemctl enable mysql

# Secure installation
sudo mysql_secure_installation
```

### 2. Create Database and User

```bash
# Login to MySQL
mysql -u root -p
```

Execute the following SQL commands:

```sql
-- Create database
CREATE DATABASE student_risk_monitoring CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Create user (replace 'your_password' with a strong password)
CREATE USER 'student_risk_user'@'localhost' IDENTIFIED BY 'your_password';

-- Grant privileges
GRANT ALL PRIVILEGES ON student_risk_monitoring.* TO 'student_risk_user'@'localhost';

-- Flush privileges
FLUSH PRIVILEGES;

-- Verify
SHOW DATABASES;
SELECT User, Host FROM mysql.user;

-- Exit
EXIT;
```

### 3. Verify MySQL Connection

```bash
# Test connection
mysql -u student_risk_user -p student_risk_monitoring
```

---

## Python Environment Setup

### 1. Clone the Repository

```bash
# Clone the project
git clone <repository-url>
cd student-risk-monitoring

# Verify directory structure
ls -la
```

### 2. Create Virtual Environment

#### Windows
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\activate

# Verify activation
where python
```

#### macOS/Linux
```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Verify activation
which python
```

### 3. Upgrade pip

```bash
# Upgrade pip to latest version
python -m pip install --upgrade pip

# Verify pip version
pip --version
```

---

## Dependencies Installation

### 1. Install Python Dependencies

```bash
# Ensure virtual environment is activated
pip install -r requirements.txt
```

### 2. Verify Installation

```bash
# Check installed packages
pip list

# Verify key packages
python -c "import flask; print(f'Flask: {flask.__version__}')"
python -c "import sklearn; print(f'Scikit-learn: {sklearn.__version__}')"
python -c "import pandas; print(f'Pandas: {pandas.__version__}')"
python -c "import mysql.connector; print('MySQL Connector: OK')"
```

### 3. Dependencies Overview

| Package | Version | Purpose |
|---------|---------|---------|
| Flask | 2.3+ | Web framework |
| Flask-SQLAlchemy | 3.0+ | ORM |
| Flask-Login | 0.6+ | Authentication |
| Flask-WTF | 1.1+ | Form handling |
| mysql-connector-python | 8.0+ | MySQL driver |
| scikit-learn | 1.3+ | Machine learning |
| pandas | 2.0+ | Data manipulation |
| numpy | 1.24+ | Numerical computing |
| joblib | 1.3+ | Model persistence |
| gunicorn | 21.2+ | WSGI server |

---

## Database Configuration

### 1. Create Environment File

```bash
# Copy example environment file
cp .env.example .env
```

### 2. Configure Environment Variables

Edit the `.env` file with your settings:

```env
# Flask Configuration
FLASK_APP=main.py
FLASK_ENV=development
SECRET_KEY=your-secret-key-here-change-in-production

# Database Configuration
DB_HOST=localhost
DB_PORT=3306
DB_NAME=student_risk_monitoring
DB_USER=student_risk_user
DB_PASSWORD=your_password

# ML Model Configuration
MODEL_PATH=models/risk_model_v1.pkl
MODEL_VERSION=1.0

# Email Configuration (Optional)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password

# Application Settings
DEBUG=True
TESTING=False
LOG_LEVEL=INFO
```

### 3. Generate Secret Key

```bash
# Generate a secure secret key
python -c "import secrets; print(secrets.token_hex(32))"
```

Copy the output and paste it as your `SECRET_KEY` in the `.env` file.

---

## Application Initialization

### 1. Setup Database Schema

```bash
# Create database tables
python setup_database.py
```

Expected output:
```
✓ Database connection successful
✓ Creating tables...
✓ Table 'users' created
✓ Table 'students' created
✓ Table 'subjects' created
✓ Table 'attendance' created
✓ Table 'marks' created
✓ Table 'fees' created
✓ Table 'library_books' created
✓ Table 'library_transactions' created
✓ Table 'complaints' created
✓ Table 'predictions' created
✓ Table 'alerts' created
✓ Table 'activity_logs' created
✓ Database setup completed successfully!
```

### 2. Seed Sample Data

```bash
# Populate with sample data
python seed_data.py
```

Expected output:
```
✓ Seeding users...
✓ Seeding students...
✓ Seeding subjects...
✓ Seeding attendance records...
✓ Seeding marks...
✓ Seeding fees...
✓ Seeding library books...
✓ Seeding complaints...
✓ Sample data seeded successfully!
```

### 3. Train Initial ML Model

```bash
# Train the machine learning model
python train_initial_model.py
```

Expected output:
```
✓ Loading training data...
✓ Feature engineering...
✓ Training model...
✓ Model evaluation:
  - Accuracy: 0.85
  - Precision: 0.82
  - Recall: 0.79
  - F1-Score: 0.80
✓ Model saved to models/risk_model_v1.pkl
✓ Training completed successfully!
```

### 4. Verify Setup

```bash
# Run tests to verify everything is working
python run_tests.py
```

---

## Running the Application

### 1. Development Mode

```bash
# Ensure virtual environment is activated
# Windows: venv\Scripts\activate
# macOS/Linux: source venv/bin/activate

# Run the application
python main.py
```

Expected output:
```
 * Serving Flask app 'main'
 * Debug mode: on
 * Running on http://127.0.0.1:5000
 * Press CTRL+C to quit
```

### 2. Access the Application

Open your web browser and navigate to:
```
http://localhost:5000
```

### 3. Default Login Credentials

| Role | Email | Password |
|------|-------|----------|
| Admin | admin@example.com | admin123 |
| Teacher | teacher@example.com | teacher123 |
| Student | student@example.com | student123 |

### 4. Production Mode (Gunicorn)

```bash
# Install gunicorn (if not already installed)
pip install gunicorn

# Run with gunicorn
gunicorn --bind 0.0.0.0:5000 --workers 4 main:app
```

### 5. Using Make Commands

```bash
# Install dependencies
make install

# Setup database
make setup

# Run application
make run

# Run tests
make test

# Seed data
make seed

# Train model
make train

# Clean temporary files
make clean
```

---

## Troubleshooting

### Common Issues and Solutions

#### 1. MySQL Connection Error

**Error**: `mysql.connector.errors.InterfaceError: 2003: Can't connect to MySQL server`

**Solutions**:
```bash
# Check if MySQL is running
# Windows
net start MySQL80

# macOS
brew services list | grep mysql

# Linux
sudo systemctl status mysql

# Verify MySQL is listening on port 3306
# Windows
netstat -an | findstr 3306

# macOS/Linux
netstat -an | grep 3306
```

#### 2. Module Not Found Error

**Error**: `ModuleNotFoundError: No module named 'flask'`

**Solutions**:
```bash
# Ensure virtual environment is activated
# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

#### 3. Database Already Exists Error

**Error**: `mysql.connector.errors.DatabaseError: 1007: Can't create database`

**Solutions**:
```bash
# Drop existing database and recreate
mysql -u root -p

DROP DATABASE IF EXISTS student_risk_monitoring;
CREATE DATABASE student_risk_monitoring CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
EXIT;

# Run setup again
python setup_database.py
```

#### 4. Permission Denied Error

**Error**: `PermissionError: [Errno 13] Permission denied`

**Solutions**:
```bash
# Check file permissions
ls -la

# Fix permissions (macOS/Linux)
chmod +x main.py
chmod -R 755 app/

# Run as administrator (Windows)
# Right-click Command Prompt -> Run as administrator
```

#### 5. Port Already in Use

**Error**: `OSError: [Errno 98] Address already in use`

**Solutions**:
```bash
# Find process using port 5000
# Windows
netstat -ano | findstr :5000

# macOS/Linux
lsof -i :5000

# Kill the process
# Windows
taskkill /PID <PID> /F

# macOS/Linux
kill -9 <PID>

# Or use a different port
python main.py --port 5001
```

#### 6. ML Model Not Found

**Error**: `FileNotFoundError: [Errno 2] No such file or directory: 'models/risk_model_v1.pkl'`

**Solutions**:
```bash
# Create models directory
mkdir -p models

# Train the model
python train_initial_model.py

# Verify model exists
ls -la models/
```

#### 7. Import Error with MySQL Connector

**Error**: `ImportError: No module named 'mysql.connector'`

**Solutions**:
```bash
# Reinstall mysql-connector-python
pip uninstall mysql-connector-python
pip install mysql-connector-python

# Or try alternative connector
pip install PyMySQL
```

#### 8. Static Files Not Loading

**Error**: CSS/JS files not loading in browser

**Solutions**:
```bash
# Check static directory structure
ls -la app/static/

# Clear browser cache
# Chrome: Ctrl+Shift+Delete -> Clear cache

# Check Flask static folder configuration
# Verify in app/__init__.py
```

### Getting Help

If you encounter issues not covered here:

1. **Check the logs**: Look for error messages in the terminal
2. **Search existing issues**: Check GitHub Issues for similar problems
3. **Create a new issue**: Provide detailed error messages and steps to reproduce
4. **Contact support**: Email the project maintainers

### Debug Mode

Enable debug mode for detailed error messages:

```env
# In .env file
FLASK_ENV=development
DEBUG=True
```

### Logging

View application logs:

```bash
# Run with verbose logging
python main.py --verbose

# Check log files
tail -f logs/app.log
```

---

## Next Steps

After successful installation:

1. **Explore the Dashboard**: Login and familiarize yourself with the interface
2. **Review Documentation**: Read the [User Manual](docs/USER_MANUAL.md)
3. **Configure Alerts**: Set up email notifications for risk alerts
4. **Train Custom Models**: Use your own data to train ML models
5. **Deploy to Production**: Follow the [Deployment Guide](DEPLOYMENT_GUIDE.md)

---

## Additional Resources

- [Project README](PROJECT_README.md)
- [API Documentation](docs/API_DOCUMENTATION.md)
- [User Manual](docs/USER_MANUAL.md)
- [Deployment Guide](DEPLOYMENT_GUIDE.md)
- [Contributing Guidelines](PROJECT_README.md#contributing)

---

**Last Updated**: 2024
**Version**: 1.0.0
