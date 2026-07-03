#!/usr/bin/env python3
"""
MySQL Database Setup Script
Intelligent Student Risk Monitoring & Decision Support System
Applies schema.sql to student_risk_monitoring DB
"""

import os
import sys
import mysql.connector
from pathlib import Path
import logging
from mysql.connector import Error

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_mysql_config():
    """Get MySQL connection config from env or prompt."""
    config = {
        'host': os.environ.get('MYSQL_HOST', 'localhost'),
        'port': int(os.environ.get('MYSQL_PORT', 3306)),
        'user': os.environ.get('MYSQL_USER', 'root'),
        'database': 'student_risk_monitoring'
    }
    
    # Password from env or prompt (secure input)
    config['password'] = os.environ.get('MYSQL_PASSWORD')
    if not config['password']:
        from getpass import getpass
        config['password'] = getpass("Enter MySQL root password (hidden): ")
    
    return config

def read_schema_file():
    """Read and prepare schema.sql"""
    schema_path = Path('database/schema.sql')
    if not schema_path.exists():
        raise FileNotFoundError(f"Schema file not found: {schema_path}")
    
    with open(schema_path, 'r', encoding='utf-8') as f:
        sql_content = f.read()
    
    # Split into statements (handle DELIMITER changes simply)
    statements = []
    current_stmt = ''
    for line in sql_content.splitlines():
        if line.strip().endswith(';') and not line.strip().startswith('--'):
            current_stmt += line + '\n'
            statements.append(current_stmt.strip())
            current_stmt = ''
        else:
            current_stmt += line + '\n'
    
    # Add remaining
    if current_stmt.strip():
        statements.append(current_stmt.strip())
    
    return statements

def apply_schema(connection, statements):
    """Execute schema statements"""
    cursor = connection.cursor()
    success_count = 0
    
    for i, stmt in enumerate(statements, 1):
        stmt = stmt.strip()
        if not stmt or stmt.startswith('--') or 'DELIMITER' in stmt:
            continue
        
        try:
            cursor.execute(stmt, multi=True)
            success_count += 1
            logger.info(f"✓ Executed statement {i}/{len(statements)}")
        except Error as e:
            logger.warning(f"⚠ Statement {i} warning: {e}")
    
    connection.commit()
    cursor.close()
    return success_count

def verify_tables(connection):
    """Verify key tables exist"""
    cursor = connection.cursor()
    cursor.execute("SHOW TABLES;")
    tables = [row[0] for row in cursor.fetchall()]
    
    expected = ['users', 'students', 'subjects', 'attendance', 'marks']
    missing = [t for t in expected if t not in tables]
    
    cursor.close()
    if missing:
        logger.error(f"Missing tables: {missing}")
        return False
    
    logger.info(f"✓ Verified {len(tables)} tables including all key tables")
    return True

def main():
    print("\n" + "="*60)
    print("MySQL Schema Setup - Student Risk Monitoring System")
    print("Target DB: student_risk_monitoring")
    print("="*60 + "\n")
    
    config = get_mysql_config()
    
    try:
        connection = mysql.connector.connect(**config)
        if connection.is_connected():
            db_info = connection.get_server_info()
            logger.info(f"Connected to MySQL {db_info} on {config['host']}:{config['port']}")
            
            # Backup warning
            print("\n⚠  WARNING: This applies schema to existing DB. Backup first if needed!")
            confirm = input("Continue? (y/N): ").lower()
            if confirm != 'y':
                print("Aborted.")
                return 1
            
            statements = read_schema_file()
            success_count = apply_schema(connection, statements)
            
            if verify_tables(connection):
                logger.info(f"\n✅ Schema applied successfully! {success_count} statements executed.")
                print("\nNext steps:")
                print("1. python setup_database.py  # sample data")
                print("2. Update .env with DATABASE_URL")
                print("3. python main.py")
            else:
                logger.error("❌ Verification failed.")
                return 1
                
    except Error as e:
        logger.error(f"❌ MySQL Error: {e}")
        return 1
    finally:
        if connection.is_connected():
            connection.close()
    
    return 0

if __name__ == '__main__':
    sys.exit(main())

