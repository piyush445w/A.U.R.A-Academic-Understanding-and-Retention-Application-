# Detailed Setup and Installation Guide

## A.U.R.A - Academic Understanding and Retention Application

This guide provides step-by-step instructions for setting up and installing the A.U.R.A - Academic Understanding and Retention Application.

## Table of Contents
1. [System Requirements](#system-requirements)
2. [Prerequisites](#prerequisites)
3. [Installation Steps](#installation-steps)
4. [Configuration](#configuration)
5. [Database Setup](#database-setup)
6. [Running the Application](#running-the-application)
7. [Deployment Options](#deployment-options)
8. [Troubleshooting](#troubleshooting)
9. [Maintenance](#maintenance)

## System Requirements

### Hardware Requirements
- **Minimum**: 
  - CPU: Dual-core 2.0 GHz
  - RAM: 4 GB
  - Storage: 10 GB available space
- **Recommended**:
  - CPU: Quad-core 2.5 GHz or better
  - RAM: 8 GB or more
  - Storage: 20 GB SSD or better

### Software Requirements
- **Operating System**: 
  - Windows 10/11 (64-bit)
  - Ubuntu Linux 20.04 LTS or later
  - macOS 10.15 or later
- **Python**: 3.8 or higher (3.9+ recommended)
- **Database**: MySQL 8.0 or higher
- **Web Browser**: Modern browser (Chrome, Firefox, Safari, Edge)

## Prerequisites

Before installing the system, ensure you have the following installed:

### 1. Python 3.8+
Download from: https://www.python.org/downloads/

Verify installation:
```bash
python --version
# Should show Python 3.8 or higher
```

### 2. MySQL Server 8.0+
Download from: https://dev.mysql.com/downloads/mysql/

During installation:
- Set root password (remember it for configuration)
- Choose UTF-8 as default character set
- Install MySQL Workbench (optional but recommended)

### 3. Git (for version control)
Download from: https://git-scm.com/downloads

Verify installation:
```bash
git --version
```

### 4. pip (Python package manager)
Usually included with Python 3.4+. Verify:
```bash
pip --version
```

## Installation Steps

### Step 1: Obtain the Source Code
```bash
# Clone the repository
git clone https://github.com/your-organization/student-risk-monitoring.git
# Or download and extract the ZIP file
cd student-risk-monitoring
```

### Step 2: Create Virtual Environment
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Unix/Linux/macOS:
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
# Upgrade pip
pip install --upgrade pip

# Install required packages
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables
```bash
# Copy example environment file
cp .env.example .env

# Edit .env file with your settings
# Use Notepad, VS Code, or any text editor
```

### Step 5: Edit Configuration (if needed)
Review and adjust settings in `config.py` if necessary:
- Database connection details
- File upload paths
- Email settings
- Risk thresholds

## Configuration

### Environment Variables (.env file)
Create a `.env` file in the project root with the following variables:

```env
# Flask Settings
SECRET_KEY=your-secret-key-here-change-in-production
FLASK_ENV=development

# Database Settings
DATABASE_URL=mysql+mysqlconnector://root:your-password@localhost:3306/student_risk_monitoring

# Email Settings (for notifications)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password

# Application Settings
APP_NAME=Student Risk Monitoring System
APP_VERSION=1.0.0

# Risk Thresholds (optional - defaults in config.py)
HIGH_RISK_THRESHOLD=0.7
MEDIUM_RISK_THRESHOLD=0.4
LOW_RISK_THRESHOLD=0.2
```

### Important Configuration Notes:
1. **SECRET_KEY**: Generate a strong random key for production
2. **DATABASE_URL**: Format: `mysql+mysqlconnector://username:password@host:port/database`
3. **Email Settings**: Required for alert notifications. Use app-specific passwords for Gmail.
4. **Flask Environment**: Set to `production` for deployment

## Database Setup

### Option 1: Automatic Setup (Recommended)
The application will create the database and tables automatically on first run if they don't exist.

### Option 2: Manual Setup
```bash
# Log into MySQL
mysql -u root -p

# Create database
CREATE DATABASE student_risk_monitoring CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

# Create user (optional but recommended)
CREATE USER 'riskmonitor'@'localhost' IDENTIFIED BY 'secure-password';
GRANT ALL PRIVILEGES ON student_risk_monitoring.* TO 'riskmonitor'@'localhost';
FLUSH PRIVILEGES;

# Exit MySQL
EXIT;
```

Then update your `.env` file:
```
DATABASE_URL=mysql+mysqlconnector://riskmonitor:secure-password@localhost:3306/student_risk_monitoring
```

### Step 6: Initialize the Application
```bash
# Ensure virtual environment is activated
# Run the application
python main.py
```

Or using Flask CLI:
```bash
flask run --host=0.0.0.0 --port=5000
```

### Step 7: Verify Installation
Open your web browser and navigate to:
- http://localhost:5000 (should show welcome message)
- http://localhost:5000/health (should show health check)

## Default Login Credentials
After first startup, the system creates default users:

| Role | Username | Password | Action Required |
|------|----------|----------|-----------------|
| Admin | admin | admin123 | **Change immediately after first login** |
| Teacher | teacher1 | teacher123 | **Change immediately after first login** |
| Student | student1 | student123 | **Change immediately after first login** |

## Deployment Options

### Development Mode
```bash
# Set environment
export FLASK_ENV=development  # Linux/macOS
set FLASK_ENV=development     # Windows

# Run with debug mode
python main.py
# or
flask run --host=0.0.0.0 --port=5000 --debug
```

### Production Mode
For production deployment, use a WSGI server:

#### Using Gunicorn (Linux/macOS)
```bash
# Install gunicorn
pip install gunicorn

# Run application
gunicorn --bind 0.0.0.0:5000 --workers 4 "app:create_app()"
```

#### Using Waitress (Windows)
```bash
# Install waitress
pip install waitress

# Run application
waitress-serve --host=0.0.0.0 --port=5000 "app:create_app()"
```

#### Using Docker (Optional)
Create a Dockerfile:
```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

ENV FLASK_ENV=production
ENV PYTHONUNBUFFERED=1

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "app:create_app()"]
```

Build and run:
```bash
docker build -t student-risk-monitoring .
docker run -p 5000:5000 --env-file .env student-risk-monitoring
```

## Troubleshooting

### Common Issues and Solutions

#### 1. Database Connection Errors
**Symptoms**: 
- "Can't connect to MySQL server"
- "Access denied for user"

**Solutions**:
- Verify MySQL service is running
- Check username/password in `.env`
- Ensure database exists
- Check firewall settings (port 3306)

#### 2. Module Import Errors
**Symptoms**:
- "ModuleNotFoundError: No module named 'X'"

**Solutions**:
- Ensure virtual environment is activated
- Reinstall dependencies: `pip install -r requirements.txt`
- Check Python version compatibility

#### 3. Port Already in Use
**Symptoms**:
- "Address already in use"
- "Port 5000 is already allocated"

**Solutions**:
- Change port in command: `flask run --port=5001`
- Stop existing process using port 5000
- Use different host/port combination

#### 4. Permission Errors
**Symptoms**:
- "Permission denied" when accessing files
- "Cannot write to directory"

**Solutions**:
- Run command prompt/terminal as administrator (Windows)
- Check folder permissions for uploads, logs, etc.
- Ensure application has write access to necessary directories

#### 5. Email Notification Failures
**Symptoms**:
- Alerts not being sent via email
- SMTP authentication errors

**Solutions**:
- Verify email credentials in `.env`
- Check if less secure apps are allowed (for Gmail)
- Use app-specific password instead of regular password
- Verify SMTP server and port settings

## Maintenance

### Regular Tasks
1. **Backup Database**: Regularly backup the `student_risk_monitoring` database
2. **Update Dependencies**: Periodically run `pip list --outdated` and update packages
3. **Check Logs**: Monitor application logs for errors or warnings
4. **Clean Uploads**: Periodically clean old files in upload directories
5. **Security Updates**: Keep system and dependencies updated

### Backup and Recovery
```bash
# Backup database
mysqldump -u root -p student_risk_monitoring > backup_$(date +%Y%m%d).sql

# Restore database
mysql -u root -p student_risk_monitoring < backup_file.sql
```

### Updating the Application
```bash
# Pull latest changes
git pull origin main

# Reinstall dependencies (if requirements changed)
pip install -r requirements.txt

# Run database migrations (if any)
# Application handles this automatically on startup
```

### Monitoring Performance
- Check response times using browser developer tools
- Monitor database query performance
- Check system resource usage (CPU, memory, disk)
- Review activity logs for unusual patterns

## Security Considerations

### 1. Initial Setup
- Change default passwords immediately
- Use strong, unique passwords for all accounts
- Restrict database access to necessary IP addresses

### 2. Ongoing Security
- Keep system and dependencies updated
- Regularly review user access and permissions
- Monitor login attempts and audit logs
- Implement HTTPS in production (using reverse proxy like Nginx)

### 3. Data Protection
- Regularly backup encrypted backups
- Ensure compliance with data protection regulations (FERPA, GDPR if applicable)
- Limit data retention as per institutional policies

## Support and Resources

### Documentation
- API Documentation: `docs/API_DOCUMENTATION.md`
- User Manual: `docs/USER_MANUAL.md`
- ER Diagram: `docs/ER_DIAGRAM.md`
- Data Flow Diagrams: `docs/DFD_LEVEL_0.md` and `docs/DFD_LEVEL_1.md`

### Community Support
- GitHub Issues: For bug reports and feature requests
- Email Support: support@studentrisksystem.edu
- Documentation Wiki: [Link to internal wiki if available]

### Professional Support
For enterprise deployments, contact:
- Email: enterprise@studentrisksystem.edu
- Phone: +1-800-STUDENT
- Website: https://studentrisksystem.edu/support

## Verification Checklist

After installation, verify the following:

[ ] Application starts without errors
[ ] Database connection successful
[ ] Default login credentials work
[ ] Role-based access control functions
[ ] Core features accessible (attendance, marks, fees, etc.)
[ ] Email notifications configured (if enabled)
[ ] File uploads working
[ ] Reports and dashboards display correctly
[ ] Alert generation functioning
[ ] API endpoints responding correctly

## Conclusion

Once you've completed these steps, your A.U.R.A - Academic Understanding and Retention Application should be fully operational. For any issues not covered in this guide, consult the troubleshooting section or contact support.

Remember to:
1. Change default passwords immediately
2. Regularly backup your data
3. Keep the system updated
4. Monitor logs for any unusual activity

For production deployments, consider additional security measures such as HTTPS, firewalls, and intrusion detection systems.