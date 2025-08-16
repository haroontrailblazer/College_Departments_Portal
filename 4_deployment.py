"""
Enhanced Deployment Script for Modern College Extension Application
Creates executables for the enhanced version with modern GUI
"""

import os
import subprocess
import sys
import shutil

def check_python_and_pip():
    """Check Python and pip installation"""
    try:
        python_version = sys.version
        print(f"Python version: {python_version}")

        result = subprocess.run([sys.executable, "-m", "pip", "--version"],
                               capture_output=True, text=True)
        print(f"Pip version: {result.stdout.strip()}")
        return True
    except Exception as e:
        print(f"Error checking Python/pip: {e}")
        return False

def install_pyinstaller():
    """Install PyInstaller using pip"""
    print("Installing PyInstaller...")
    try:
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", "--upgrade", "pyinstaller"
        ], check=True, capture_output=True, text=True)

        print("PyInstaller installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Failed to install PyInstaller: {e}")
        return False

def test_pyinstaller():
    """Test if PyInstaller is accessible"""
    print("Testing PyInstaller installation...")

    try:
        result = subprocess.run([sys.executable, "-m", "PyInstaller", "--version"],
                               capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print(f"PyInstaller version: {result.stdout.strip()}")
            return "module"
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
        pass

    print("PyInstaller not accessible")
    return None

def create_executable(file_name, app_name, method="module", windowed=False):
    """Create executable using the specified method"""
    print(f"Creating {app_name} executable...")

    cmd = [sys.executable, "-m", "PyInstaller"]

    # Add PyInstaller arguments
    cmd.extend([
        "--onefile",
        "--name", app_name,
        file_name
    ])

    if windowed:
        cmd.append("--windowed")
    else:
        cmd.append("--console")

    try:
        print(f"Running: {' '.join(cmd)}")
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(f"✓ Successfully created {app_name}.exe")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed to create {app_name}.exe")
        print(f"Error: {e.stderr}")
        return False

def create_all_executables():
    """Create all executable files"""
    print("\n" + "="*60)
    print("CREATING ENHANCED APPLICATION EXECUTABLES")
    print("="*60)

    method = test_pyinstaller()
    if not method:
        return False

    # Files to convert (enhanced versions)
    files_to_convert = [
        ("1_setup_database.py", "DatabaseSetup", False),
        ("2_server.py", "EnhancedCollegeServer", False),
        ("3_client_gui.py", "EnhancedCollegeClient", True)
    ]

    success_count = 0
    for file_name, app_name, windowed in files_to_convert:
        if os.path.exists(file_name):
            if create_executable(file_name, app_name, method, windowed):
                success_count += 1
        else:
            print(f"Warning: {file_name} not found, skipping...")

    print(f"\nSuccessfully created {success_count} out of {len(files_to_convert)} executables")
    return success_count > 0

def create_deployment_package():
    """Create enhanced deployment package"""
    print("\nCreating enhanced deployment package...")

    deploy_dir = "enhanced_college_extension_deployment"
    if os.path.exists(deploy_dir):
        shutil.rmtree(deploy_dir)
    os.makedirs(deploy_dir)

    # Copy executables
    exe_files = [
        "dist/DatabaseSetup.exe",
        "dist/EnhancedCollegeServer.exe",
        "dist/EnhancedCollegeClient.exe"
    ]

    copied_files = 0
    for exe_file in exe_files:
        if os.path.exists(exe_file):
            shutil.copy2(exe_file, deploy_dir)
            print(f"Copied {os.path.basename(exe_file)} to deployment directory")
            copied_files += 1
        else:
            print(f"Warning: {exe_file} not found")

    # Copy database file if it exists
    if os.path.exists("college_data.db"):
        shutil.copy2("college_data.db", deploy_dir)
        print("Copied database to deployment directory")

    # Create enhanced batch files
    create_enhanced_batch_files(deploy_dir)

    # Create enhanced README
    create_enhanced_readme(deploy_dir)

    print(f"\nEnhanced deployment package created with {copied_files} executables")
    print(f"Location: {os.path.abspath(deploy_dir)}")

def create_enhanced_batch_files(deploy_dir):
    """Create enhanced batch files"""

    # Setup batch file
    with open(os.path.join(deploy_dir, "1_Setup_Database.bat"), 'w') as f:
        f.write('''@echo off
title College Extension - Database Setup
color 0A
echo.
echo ===============================================
echo    COLLEGE EXTENSION DATABASE SETUP
echo ===============================================
echo.
echo Setting up SQLite database and sample data...
echo.
DatabaseSetup.exe
echo.
echo ===============================================
echo Database setup completed successfully!
echo ===============================================
echo.
echo Press any key to continue...
pause > nul
''')

    # Enhanced server batch file
    with open(os.path.join(deploy_dir, "2_Start_Enhanced_Server.bat"), 'w') as f:
        f.write('''@echo off
title College Extension - Enhanced Server
color 0B
echo.
echo ===============================================
echo    COLLEGE EXTENSION - ENHANCED SERVER
echo ===============================================
echo.
echo Features:
echo * Auto CSV export on every data entry
echo * Real-time activity monitoring  
echo * Enhanced logging and security
echo * Multi-threaded client handling
echo * Extended connection timeout (60 seconds)
echo.
echo Server will start on port 9999
echo Keep this window open while using the system
echo.
echo ===============================================
echo.
EnhancedCollegeServer.exe
echo.
echo ===============================================
echo Server has stopped.
echo ===============================================
pause
''')

    # Enhanced client batch file
    with open(os.path.join(deploy_dir, "3_Start_Enhanced_Client.bat"), 'w') as f:
        f.write('''@echo off
title College Extension - Enhanced Client
color 0E
echo.
echo ===============================================
echo    COLLEGE EXTENSION - ENHANCED CLIENT
echo ===============================================
echo.
echo Features:
echo * Modern full-screen interface
echo * Enter key for quick data submission
echo * Real-time activity updates
echo * Auto CSV generation
echo * Enhanced status monitoring
echo.
echo Launching enhanced client application...
echo.
start EnhancedCollegeClient.exe
echo.
echo Enhanced client application launched!
echo ===============================================
''')

def create_enhanced_readme(deploy_dir):
    """Create enhanced README file"""
    readme_content = '''Enhanced College Extension Application - Deployment Package


NEW ENHANCED FEATURES:
• Modern full-screen interface with professional design
• Enter key support for quick data submission
• Automatic CSV export on every data entry
• Real-time activity monitoring and updates
• Enhanced status logging with color coding
• Improved keyboard shortcuts and user experience
• Auto-refresh functionality for live updates

QUICK START:
1. Run "1_Setup_Database.bat" first (one-time setup)
2. Run "2_Start_Enhanced_Server.bat" on the main server computer
3. Run "3_Start_Enhanced_Client.bat" on each department computer

SAMPLE LOGIN CREDENTIALS:

Department        Email                    Password

Computer Science  cs@college.edu          cs_password123
Mathematics       math@college.edu        math_password123  
Physics           physics@college.edu     physics_password123
Chemistry         chemistry@college.edu   chemistry_password123
Biology           bio@college.edu         bio_password123
English           english@college.edu     english_password123


KEYBOARD SHORTCUTS:
• Enter / Ctrl+Enter: Submit data
• F5: Refresh activity
• Ctrl+L: Focus on login
• Escape: Clear data entry

NETWORK SETUP:
• Default server port: 9999
• Auto-connection to server on client startup
• Extended connection timeout (60 seconds)
• For multiple computers, update server IP in client
• Ensure Windows Firewall allows the applications
• Server supports multiple simultaneous connections

AUTO CSV EXPORT:
• CSV files are automatically generated after each data entry
• Timestamped files: college_data_export_YYYYMMDD_HHMMSS.csv  
• Latest export: latest_college_data_export.csv
• Manual export still available via Export CSV button

ENHANCED INTERFACE:
• Full-screen modern design with professional styling
• Real-time connection status indicator
• Activity monitoring panel showing recent submissions
• Enhanced error handling and user feedback
• Responsive layout that adapts to screen size

TROUBLESHOOTING:
• Connection issues: Check server IP address and firewall
• Login problems: Verify credentials and server connection
• Data not saving: Ensure all fields are completed
• CSV not generating: Check server permissions and disk space

FILES INCLUDED:
• DatabaseSetup.exe: Database initialization
• EnhancedCollegeServer.exe: Enhanced server with auto-features  
• EnhancedCollegeClient.exe: Modern client with full-screen GUI
• college_data.db: SQLite database file
• Enhanced batch files for easy execution

SUPPORT:
For technical support or feature requests, refer to the enhanced
user documentation or contact your system administrator.

===============================================
Enhanced College Extension Application v2.0
Professional Data Management for Educational Institutions
===============================================
'''

    with open(os.path.join(deploy_dir, "README.txt"), 'w') as f:
        f.write(readme_content)

def cleanup_build_files():
    """Clean up PyInstaller build files"""
    print("\nCleaning up build files...")

    dirs_to_remove = ["build", "__pycache__"]
    files_to_remove = []

    # Find .spec files
    for file in os.listdir('.'):
        if file.endswith('.spec'):
            files_to_remove.append(file)

    # Remove directories
    for dir_name in dirs_to_remove:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"Removed {dir_name} directory")

    # Remove files
    for file_name in files_to_remove:
        if os.path.exists(file_name):
            os.remove(file_name)
            print(f"Removed {file_name}")

def main():
    print("="*70)
    print("ENHANCED COLLEGE EXTENSION APPLICATION - DEPLOYMENT SCRIPT")
    print("="*70)
    print("Creating modern, full-featured version with:")
    print("• Professional full-screen GUI")
    print("• Auto-connection to server")
    print("• Enter key support for data submission") 
    print("• Automatic CSV export on every entry")
    print("• Real-time activity monitoring")
    print("• Extended connection timeout (60s)")
    print("• Enhanced user experience")
    print("="*70)

    # Check Python and pip
    if not check_python_and_pip():
        print(" Python/pip check failed. Please ensure Python is properly installed.")
        return

    # Install/upgrade PyInstaller
    if not install_pyinstaller():
        print(" Failed to install PyInstaller. Please check your internet connection.")
        return

    # Create executables
    if not create_all_executables():
        print(" Failed to create executables.")
        return

    # Create deployment package
    create_deployment_package()

    # Cleanup
    cleanup_build_files()

    print("\n" + "="*70)
    print("ENHANCED DEPLOYMENT COMPLETED SUCCESSFULLY!")
    print("="*70)
    print("\nFeatures included:")
    print("   • Modern full-screen interface")
    print("   • Auto-connection to server")
    print("   • Enter key for quick data submission")
    print("   • Auto CSV export on every data entry")
    print("   • Real-time activity updates")
    print("   • Extended connection timeout (60s)")
    print("   • Professional styling and UX")
    print("\n Next steps:")
    print("   1. Go to 'enhanced_college_extension_deployment' folder")
    print("   2. Follow the enhanced instructions in README.txt")
    print("   3. Run the batch files in order")
    print("\n Your enhanced application is ready for deployment!")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n Deployment cancelled by user.")
    except Exception as e:
        print(f"\n Unexpected error: {e}")
        print("Please check your Python installation and try again.")
