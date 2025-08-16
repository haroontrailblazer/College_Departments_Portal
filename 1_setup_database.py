"""
Enhanced Database Setup Script
Run this first to create the database and sample data
Now with better error handling and validation
"""

import sqlite3
import hashlib
import os
from datetime import datetime

def create_database():
    """Create the main database with necessary tables"""
    try:
        conn = sqlite3.connect('college_data.db')
        cursor = conn.cursor()

        # Create departments table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS departments (
            dept_id INTEGER PRIMARY KEY AUTOINCREMENT,
            dept_name TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        # Create data_entries table for storing department data
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS data_entries (
            entry_id INTEGER PRIMARY KEY AUTOINCREMENT,
            dept_id INTEGER,
            entry_type TEXT NOT NULL,
            data_content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (dept_id) REFERENCES departments (dept_id)
        )
        """)

        # Create system_logs table for better tracking
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS system_logs (
            log_id INTEGER PRIMARY KEY AUTOINCREMENT,
            log_level TEXT NOT NULL,
            message TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        conn.commit()
        conn.close()
        print("✓ Database created successfully!")
        return True

    except Exception as e:
        print(f"✗ Error creating database: {e}")
        return False

def add_sample_departments():
    """Add some sample departments for testing"""
    try:
        conn = sqlite3.connect('college_data.db')
        cursor = conn.cursor()

        # Sample departments with better organization
        departments = [
            ('Computer Science', 'cs@college.edu', 'cs_password123'),
            ('Mathematics', 'math@college.edu', 'math_password123'),
            ('Physics', 'physics@college.edu', 'physics_password123'),
            ('Chemistry', 'chemistry@college.edu', 'chem_password123'),
            ('Biology', 'bio@college.edu', 'bio_password123'),
            ('English', 'english@college.edu', 'eng_password123'),
            ('Engineering', 'eng@college.edu', 'eng_password123'),
            ('Business', 'business@college.edu', 'business_password123')
        ]

        added_count = 0
        for dept_name, email, password in departments:
            # Hash the password using SHA256 (use bcrypt in production)
            password_hash = hashlib.sha256(password.encode()).hexdigest()

            try:
                cursor.execute("""
                INSERT INTO departments (dept_name, email, password_hash)
                VALUES (?, ?, ?)
                """, (dept_name, email, password_hash))
                print(f"✓ Added department: {dept_name}")
                added_count += 1
            except sqlite3.IntegrityError:
                print(f"⚠ Department {dept_name} already exists")

        conn.commit()
        conn.close()
        print(f"✓ Sample departments setup completed! ({added_count} new departments added)")
        return True

    except Exception as e:
        print(f"✗ Error adding sample departments: {e}")
        return False

def display_sample_credentials():
    """Display sample login credentials in a formatted table"""
    print("\n" + "="*70)
    print("SAMPLE LOGIN CREDENTIALS")
    print("="*70)

    try:
        conn = sqlite3.connect('college_data.db')
        cursor = conn.cursor()

        cursor.execute('SELECT dept_name, email FROM departments ORDER BY dept_name')
        departments = cursor.fetchall()
        conn.close()

        # Create formatted table
        print(f"{'Department':<18} {'Email':<25} {'Password':<20}")
        print("-" * 70)

        for dept_name, email in departments:
            # Extract password from email (this is just for demo purposes)
            password = email.split('@')[0] + "_password123"
            print(f"{dept_name:<18} {email:<25} {password:<20}")

        print("=" * 70)
        print("⚠ NOTE: These are sample credentials for testing only.")
        print("🔐 In production, use strong, unique passwords for each department.")
        return True

    except Exception as e:
        print(f"✗ Error displaying credentials: {e}")
        return False

if __name__ == "__main__":
    print("="*70)
    print("ENHANCED COLLEGE EXTENSION APPLICATION - DATABASE SETUP")
    print("="*70)
    print(f"Setup started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # Check if database already exists
    if os.path.exists('college_data.db'):
        print("⚠ Database already exists. Creating backup...")
        backup_name = f'college_data_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.db'
        try:
            if os.path.exists(backup_name):
                os.remove(backup_name)
            os.rename('college_data.db', backup_name)
            print(f"✓ Backup created: {backup_name}")
        except Exception as e:
            print(f"⚠ Backup failed: {e}")

    success_count = 0

    # Create database
    if create_database():
        success_count += 1

        # Add departments
        if add_sample_departments():
            success_count += 1

            # Display credentials
            if display_sample_credentials():
                success_count += 1

    print("\n" + "="*70)
    if success_count >= 2:
        print("✅ DATABASE SETUP COMPLETED SUCCESSFULLY!")
        print("="*70)
        print("\nNext steps:")
        print("1. Start the server: python 2_server.py")
        print("2. Run the client GUI: python 3_client_gui.py")
        print("3. Or create executables: python 4_deployment.py")
        print("\n🚀 Your enhanced College Extension Application is ready!")
    else:
        print("❌ DATABASE SETUP ENCOUNTERED ISSUES!")
        print("Please check the error messages above and try again.")

    print("="*70)
