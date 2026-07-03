#!/usr/bin/env python3
"""
Application Initialization Script
Intelligent Student Risk Monitoring & Decision Support System
"""

import os
import sys
import logging
import subprocess
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app_init.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


def check_dependencies():
    """
    Check if all required dependencies are installed.
    
    Returns:
        True if all dependencies are installed, False otherwise
    """
    try:
        logger.info("Checking dependencies...")
        
        required_packages = [
            'flask',
            'flask-sqlalchemy',
            'flask-login',
            'flask-wtf',
            'numpy',
            'pandas',
            'scikit-learn',
            'joblib',
            'python-dotenv',
            'mysql-connector-python'
        ]
        
        missing_packages = []
        
        for package in required_packages:
            try:
                __import__(package.replace('-', '_'))
                logger.info(f"✓ {package}")
            except ImportError:
                logger.warning(f"✗ {package} - NOT INSTALLED")
                missing_packages.append(package)
        
        if missing_packages:
            logger.error(f"Missing packages: {', '.join(missing_packages)}")
            logger.info("Install them using: pip install -r requirements.txt")
            return False
        
        logger.info("✓ All dependencies are installed")
        return True
    except Exception as e:
        logger.error(f"Error checking dependencies: {str(e)}")
        return False


def check_environment():
    """
    Check if environment is properly configured.
    
    Returns:
        True if environment is configured, False otherwise
    """
    try:
        logger.info("Checking environment configuration...")
        
        # Check if .env file exists
        env_file = Path('.env')
        if not env_file.exists():
            logger.warning(".env file not found")
            logger.info("Creating .env file from .env.example...")
            
            env_example = Path('.env.example')
            if env_example.exists():
                import shutil
                shutil.copy(env_example, env_file)
                logger.info("✓ Created .env file from .env.example")
            else:
                logger.warning(".env.example not found, creating default .env")
                with open(env_file, 'w') as f:
                    f.write("# Flask Configuration\n")
                    f.write("SECRET_KEY=dev-secret-key-change-in-production\n")
                    f.write("FLASK_ENV=development\n")
                    f.write("FLASK_DEBUG=1\n")
                    f.write("\n")
                    f.write("# Database Configuration\n")
                    f.write("DATABASE_URL=mysql+mysqlconnector://root:password@localhost:3306/student_risk_db\n")
                    f.write("\n")
                    f.write("# Email Configuration\n")
                    f.write("MAIL_SERVER=smtp.gmail.com\n")
                    f.write("MAIL_PORT=587\n")
                    f.write("MAIL_USE_TLS=true\n")
                    f.write("MAIL_USERNAME=\n")
                    f.write("MAIL_PASSWORD=\n")
                logger.info("✓ Created default .env file")
        
        # Load environment variables
        from dotenv import load_dotenv
        load_dotenv()
        
        # Check required environment variables
        required_vars = ['SECRET_KEY', 'DATABASE_URL']
        missing_vars = []
        
        for var in required_vars:
            if not os.environ.get(var):
                missing_vars.append(var)
        
        if missing_vars:
            logger.warning(f"Missing environment variables: {', '.join(missing_vars)}")
            logger.info("Please update .env file with required values")
        
        logger.info("✓ Environment configuration checked")
        return True
    except Exception as e:
        logger.error(f"Error checking environment: {str(e)}")
        return False


def setup_database():
    """
    Setup database.
    
    Returns:
        True if successful, False otherwise
    """
    try:
        logger.info("Setting up database...")
        
        # Run setup_database.py
        result = subprocess.run(
            [sys.executable, 'setup_database.py'],
            check=True,
            capture_output=False,
            text=True
        )
        
        if result.returncode == 0:
            logger.info("✓ Database setup completed successfully")
            return True
        else:
            logger.error("Database setup failed")
            return False
    except subprocess.CalledProcessError as e:
        logger.error(f"Error setting up database: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Error setting up database: {str(e)}")
        return False


def seed_data():
    """
    Seed sample data.
    
    Returns:
        True if successful, False otherwise
    """
    try:
        logger.info("Seeding sample data...")
        
        # Run seed_data.py
        result = subprocess.run(
            [sys.executable, 'seed_data.py'],
            check=True,
            capture_output=False,
            text=True
        )
        
        if result.returncode == 0:
            logger.info("✓ Data seeding completed successfully")
            return True
        else:
            logger.error("Data seeding failed")
            return False
    except subprocess.CalledProcessError as e:
        logger.error(f"Error seeding data: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Error seeding data: {str(e)}")
        return False


def train_model():
    """
    Train initial ML model.
    
    Returns:
        True if successful, False otherwise
    """
    try:
        logger.info("Training initial ML model...")
        
        # Run train_initial_model.py
        result = subprocess.run(
            [sys.executable, 'train_initial_model.py'],
            check=True,
            capture_output=False,
            text=True
        )
        
        if result.returncode == 0:
            logger.info("✓ Model training completed successfully")
            return True
        else:
            logger.error("Model training failed")
            return False
    except subprocess.CalledProcessError as e:
        logger.error(f"Error training model: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Error training model: {str(e)}")
        return False


def run_tests():
    """
    Run tests.
    
    Returns:
        True if successful, False otherwise
    """
    try:
        logger.info("Running tests...")
        
        # Run pytest
        result = subprocess.run(
            [sys.executable, '-m', 'pytest', 'tests/', '-v'],
            check=True,
            capture_output=False,
            text=True
        )
        
        if result.returncode == 0:
            logger.info("✓ Tests completed successfully")
            return True
        else:
            logger.warning("Some tests failed")
            return True  # Don't fail initialization if tests fail
    except subprocess.CalledProcessError as e:
        logger.warning(f"Error running tests: {str(e)}")
        return True  # Don't fail initialization if tests fail
    except Exception as e:
        logger.warning(f"Error running tests: {str(e)}")
        return True  # Don't fail initialization if tests fail


def create_directories():
    """
    Create necessary directories.
    
    Returns:
        True if successful, False otherwise
    """
    try:
        logger.info("Creating necessary directories...")
        
        directories = [
            'models/trained_models',
            'app/static/uploads',
            'logs',
            'backups'
        ]
        
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)
            logger.info(f"✓ Created directory: {directory}")
        
        return True
    except Exception as e:
        logger.error(f"Error creating directories: {str(e)}")
        return False


def start_application():
    """
    Start the Flask application.
    
    Returns:
        True if successful, False otherwise
    """
    try:
        logger.info("Starting Flask application...")
        
        # Import and run the application
        from main import app
        
        print("\n" + "="*60)
        print("Starting Flask Application")
        print("="*60)
        print("\nApplication is running at: http://localhost:5000")
        print("Press Ctrl+C to stop the application")
        print("="*60 + "\n")
        
        app.run(
            host='0.0.0.0',
            port=5000,
            debug=True,
            use_reloader=False
        )
        
        return True
    except Exception as e:
        logger.error(f"Error starting application: {str(e)}")
        return False


def main():
    """Main function to initialize application."""
    print("\n" + "="*60)
    print("Application Initialization - Student Risk Monitoring System")
    print("="*60 + "\n")
    
    # Initialization steps
    steps = [
        ("Checking dependencies", check_dependencies),
        ("Checking environment", check_environment),
        ("Creating directories", create_directories),
        ("Setting up database", setup_database),
        ("Seeding sample data", seed_data),
        ("Training initial model", train_model),
        ("Running tests", run_tests)
    ]
    
    success = True
    
    for step_name, step_function in steps:
        print(f"\n{'='*60}")
        print(f"Step: {step_name}")
        print(f"{'='*60}\n")
        
        if not step_function():
            logger.error(f"Failed at step: {step_name}")
            success = False
            
            # Ask user if they want to continue
            response = input(f"\n{step_name} failed. Do you want to continue? (y/n): ")
            if response.lower() != 'y':
                break
    
    # Print summary
    print("\n" + "="*60)
    print("Initialization Summary")
    print("="*60)
    
    if success:
        print("✓ Application initialization completed successfully")
        print("\nDefault credentials:")
        print("  Admin: admin / admin123")
        print("  Teacher: teacher / teacher123")
        print("  Student: STU001 / student123")
        print("\nStarting application...")
        
        # Start application
        start_application()
    else:
        print("✗ Application initialization failed")
        print("Check app_init.log for details")
        print("\nYou can still try to start the application manually:")
        print("  python main.py")
        return 1
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
