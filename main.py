"""
A.U.R.A - Academic Understanding and Retention Application
Main Flask Application Entry Point
"""

import os
from pathlib import Path

# Ensure we're running from the project root directory
# This is critical for SQLite database path resolution
PROJECT_ROOT = Path(__file__).resolve().parent
os.chdir(PROJECT_ROOT)

# Now import and create the app
from app import create_app

# Create the Flask application instance
app = create_app()

if __name__ == '__main__':
    # Get configuration values with fallbacks
    # FLASK_DEBUG from 
    # .env is string 'true'/'false', convert to bool
    debug_val = os.environ.get('FLASK_DEBUG', '')
    debug_mode = debug_val.lower() in ('true', '1', 'yes') if debug_val else app.config.get('DEBUG', False)
    host = os.environ.get('FLASK_HOST', app.config.get('HOST', '0.0.0.0'))
    port = int(os.environ.get('FLASK_PORT', '') or app.config.get('PORT', 5000))
    
    print(f"Starting app in {'debug' if debug_mode else 'production'} mode")
    print(f"Host: {host}, Port: {port}")
    print(f"Database: {app.config.get('SQLALCHEMY_DATABASE_URI')}")
    
    app.run(debug=debug_mode, host=host, port=port)