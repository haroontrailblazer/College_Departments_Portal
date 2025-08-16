"""
Enhanced College Extension Application - Server Component
Features: Enhanced CSV export, real-time updates, improved logging, better formatting
"""

import socket
import threading
import json
import sqlite3
import hashlib
import csv
import os
from datetime import datetime
import time
import shutil

class EnhancedCollegeServer:
    def __init__(self, host='localhost', port=9999):
        self.host = host
        self.port = port
        self.clients = []
        self.running = False
        self.stats = {'connections': 0, 'data_entries': 0, 'exports': 0}

    def authenticate_department(self, email, password):
        """Authenticate department login with better error handling"""
        try:
            conn = sqlite3.connect('college_data.db')
            cursor = conn.cursor()

            password_hash = hashlib.sha256(password.encode()).hexdigest()
            query = """
            SELECT dept_id, dept_name FROM departments
            WHERE email = ? AND password_hash = ?
            """
            cursor.execute(query, (email, password_hash))
            result = cursor.fetchone()
            conn.close()

            if result:
                self.log_activity(f"Successful login: {result[1]} ({email})")
                return {'success': True, 'dept_id': result[0], 'dept_name': result[1]}
            else:
                self.log_activity(f"Failed login attempt: {email}")
                return {'success': False, 'message': 'Invalid credentials'}

        except Exception as e:
            self.log_activity(f"Authentication error: {e}")
            return {'success': False, 'message': 'Authentication system error'}

    def save_department_data(self, dept_id, entry_type, data_content):
        """Save data entry to database and auto-export CSV with enhanced validation and error handling"""
        try:
            # Enhanced input validation
            if not dept_id:
                return {'success': False, 'message': 'Department ID is required'}
                
            if not entry_type or not entry_type.strip():
                return {'success': False, 'message': 'Entry type is required'}
                
            if not data_content or not data_content.strip():
                return {'success': False, 'message': 'Data content is required'}

            if len(data_content) > 10000:  # Limit content length
                return {'success': False, 'message': 'Content too long (max 10,000 characters)'}

            # Validate department exists
            conn = sqlite3.connect('college_data.db')
            cursor = conn.cursor()
            
            # Check if department exists
            cursor.execute("SELECT dept_name FROM departments WHERE dept_id = ?", (dept_id,))
            dept_result = cursor.fetchone()
            if not dept_result:
                conn.close()
                return {'success': False, 'message': 'Invalid department ID'}

            dept_name = dept_result[0]
            
            # Insert data entry with transaction
            try:
                query = """
                INSERT INTO data_entries (dept_id, entry_type, data_content, created_at)
                VALUES (?, ?, ?, CURRENT_TIMESTAMP)
                """
                cursor.execute(query, (dept_id, entry_type.strip(), data_content.strip()))
                entry_id = cursor.lastrowid
                
                # Commit the transaction
                conn.commit()
                
                # Update statistics
                self.stats['data_entries'] += 1
                
                self.log_activity(f"Data saved successfully: Entry ID {entry_id}, Department: {dept_name}, Type: {entry_type}")
                
            except sqlite3.Error as db_error:
                conn.rollback()
                conn.close()
                return {'success': False, 'message': f'Database error: {str(db_error)}'}
            
            finally:
                conn.close()

            # Auto-export enhanced CSV after successful data entry
            try:
                csv_result = self.auto_export_enhanced_csv()
                if csv_result:
                    self.log_activity(f"CSV auto-export successful: {csv_result}")
                else:
                    self.log_activity("CSV auto-export failed")
            except Exception as csv_error:
                self.log_activity(f"CSV auto-export error: {csv_error}")

            return {'success': True, 'entry_id': entry_id, 'dept_name': dept_name}

        except Exception as e:
            self.log_activity(f"Critical error saving data: {e}")
            return {'success': False, 'message': f'System error: {str(e)}'}

    def auto_export_enhanced_csv(self):
        """Automatically export enhanced CSV with professional formatting - returns filename on success"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'college_data_export_{timestamp}.csv'
            
            # Also create a latest version for easy access
            latest_filename = 'latest_college_data_export.csv'

            conn = sqlite3.connect('college_data.db')
            cursor = conn.cursor()

            # Get comprehensive data with statistics
            query = """
            SELECT 
                d.dept_name, 
                d.email, 
                de.entry_type, 
                de.data_content, 
                de.created_at,
                de.entry_id
            FROM data_entries de
            JOIN departments d ON de.dept_id = d.dept_id
            ORDER BY de.created_at DESC
            """
            cursor.execute(query)
            data = cursor.fetchall()

            # Get summary statistics
            cursor.execute("SELECT COUNT(*) FROM data_entries")
            total_entries = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(DISTINCT dept_id) FROM data_entries")
            active_departments = cursor.fetchone()[0]

            cursor.execute("""
            SELECT entry_type, COUNT(*) 
            FROM data_entries 
            GROUP BY entry_type 
            ORDER BY COUNT(*) DESC
            """)
            type_stats = cursor.fetchall()

            conn.close()

            # Create enhanced CSV with metadata
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)

                # Header section with metadata
                writer.writerow(['COLLEGE EXTENSION APPLICATION - DATA EXPORT'])
                writer.writerow(['=' * 60])
                writer.writerow(['Export Information'])
                writer.writerow(['Export Date/Time', datetime.now().strftime('%Y-%m-%d %H:%M:%S')])
                writer.writerow(['Total Records', total_entries])
                writer.writerow(['Active Departments', active_departments])
                writer.writerow(['Export File', filename])
                writer.writerow([])

                # Statistics section
                writer.writerow(['DATA SUMMARY BY CATEGORY'])
                writer.writerow(['-' * 30])
                writer.writerow(['Category', 'Count', 'Percentage'])
                for entry_type, count in type_stats:
                    percentage = (count / total_entries * 100) if total_entries > 0 else 0
                    writer.writerow([entry_type, count, f'{percentage:.1f}%'])
                writer.writerow([])

                # Recent activity (last 10 entries)
                cursor.execute("""
                SELECT 
                    de.created_at,
                    d.dept_name,
                    de.entry_type,
                    SUBSTR(de.data_content, 1, 100) as preview
                FROM data_entries de
                JOIN departments d ON de.dept_id = d.dept_id
                ORDER BY de.created_at DESC
                LIMIT 10
                """)
                recent_activity = cursor.fetchall()

                writer.writerow(['RECENT ACTIVITY (Last 10 Entries)'])
                writer.writerow(['-' * 50])
                writer.writerow(['Date/Time', 'Department', 'Category', 'Content Preview'])

                for created_at, dept_name, entry_type, preview in recent_activity:
                    writer.writerow([created_at, dept_name, entry_type, preview + '...'])
                writer.writerow([])

                # Main data section
                writer.writerow(['DETAILED DATA EXPORT'])
                writer.writerow(['-' * 50])
                writer.writerow(['Entry ID', 'Department', 'Email', 'Category', 'Content', 'Created At'])

                for entry_id, dept_name, email, entry_type, data_content, created_at in data:
                    # Truncate content for CSV readability
                    content_preview = data_content[:200] + '...' if len(data_content) > 200 else data_content
                    writer.writerow([entry_id, dept_name, email, entry_type, content_preview, created_at])

            # Create a copy as latest version
            shutil.copy2(filename, latest_filename)
            
            self.log_activity(f"Enhanced CSV export completed: {filename}")
            return filename

        except Exception as e:
            self.log_activity(f"Error creating CSV export: {e}")
            return None

    def export_formatted_report(self, filename='college_report.csv'):
        """Create a formatted report with advanced analytics"""
        try:
            conn = sqlite3.connect('college_data.db')
            cursor = conn.cursor()

            # Get data with analytics
            current_time = datetime.now()

            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)

                # Title and header
                writer.writerow(['COLLEGE EXTENSION APPLICATION - COMPREHENSIVE REPORT'])
                writer.writerow(['=' * 70])
                writer.writerow(['Report Generated', current_time.strftime('%Y-%m-%d %H:%M:%S')])
                writer.writerow([])

                # Department activity summary
                cursor.execute("""
                SELECT 
                    d.dept_name,
                    COUNT(de.entry_id) as total_entries,
                    MAX(de.created_at) as last_activity,
                    MIN(de.created_at) as first_activity
                FROM departments d
                LEFT JOIN data_entries de ON d.dept_id = de.dept_id
                GROUP BY d.dept_id, d.dept_name
                ORDER BY total_entries DESC
                """)
                dept_stats = cursor.fetchall()

                writer.writerow(['DEPARTMENT ACTIVITY SUMMARY'])
                writer.writerow(['-' * 40])
                writer.writerow(['Department', 'Total Entries', 'First Activity', 'Last Activity', 'Status'])

                for dept_name, total_entries, last_activity, first_activity in dept_stats:
                    status = 'Active' if total_entries > 0 else 'No Data'
                    writer.writerow([dept_name, total_entries or 0, first_activity or 'N/A', last_activity or 'N/A', status])

                writer.writerow([])

                # Recent activity (last 10 entries)
                cursor.execute("""
                SELECT 
                    de.created_at,
                    d.dept_name,
                    de.entry_type,
                    SUBSTR(de.data_content, 1, 100) as preview
                FROM data_entries de
                JOIN departments d ON de.dept_id = d.dept_id
                ORDER BY de.created_at DESC
                LIMIT 10
                """)
                recent_activity = cursor.fetchall()

                writer.writerow(['RECENT ACTIVITY (Last 10 Entries)'])
                writer.writerow(['-' * 50])
                writer.writerow(['Date/Time', 'Department', 'Category', 'Content Preview'])

                for created_at, dept_name, entry_type, preview in recent_activity:
                    writer.writerow([created_at, dept_name, entry_type, preview + '...'])

            conn.close()
            return filename

        except Exception as e:
            self.log_activity(f"Error creating report: {e}")
            return None

    def get_recent_entries(self, limit=10):
        """Get recent entries for real-time updates"""
        try:
            conn = sqlite3.connect('college_data.db')
            cursor = conn.cursor()

            query = """
            SELECT 
                d.dept_name, 
                de.entry_type, 
                SUBSTR(de.data_content, 1, 100) as content_preview, 
                de.created_at
            FROM data_entries de
            JOIN departments d ON de.dept_id = d.dept_id
            ORDER BY de.created_at DESC
            LIMIT ?
            """
            cursor.execute(query, (limit,))
            data = cursor.fetchall()
            conn.close()

            return [{
                'dept_name': row[0], 
                'entry_type': row[1], 
                'content_preview': row[2], 
                'created_at': row[3]
            } for row in data]

        except Exception as e:
            self.log_activity(f"Error getting recent entries: {e}")
            return []

    def log_activity(self, message):
        """Enhanced logging with timestamp"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_message = f"[{timestamp}] {message}"
        print(log_message)

        # Also log to database
        try:
            conn = sqlite3.connect('college_data.db')
            cursor = conn.cursor()
            cursor.execute("""
            INSERT INTO system_logs (log_level, message)
            VALUES (?, ?)
            """, ('INFO', message))
            conn.commit()
            conn.close()
        except:
            pass  # Don't let logging errors crash the system

    def handle_client(self, client_socket, address):
        """Handle individual client connection with better error handling"""
        self.stats['connections'] += 1
        self.log_activity(f"New connection from {address[0]}:{address[1]}")

        authenticated = False
        dept_info = None

        try:
            while True:
                # Set timeout to prevent hanging connections (increased from 30 to 60 seconds)
                client_socket.settimeout(60.0)

                try:
                    data = client_socket.recv(1024).decode('utf-8')
                    if not data:
                        break
                except socket.timeout:
                    self.log_activity(f"Client {address} timed out after 60 seconds")
                    break
                except ConnectionResetError:
                    self.log_activity(f"Client {address} disconnected unexpectedly")
                    break

                try:
                    message = json.loads(data)
                    action = message.get('action')

                    if action == 'login' and not authenticated:
                        email = message.get('email', '').strip()
                        password = message.get('password', '').strip()

                        if not email or not password:
                            response = {
                                'status': 'error',
                                'message': 'Email and password required'
                            }
                        else:
                            auth_result = self.authenticate_department(email, password)
                            if auth_result['success']:
                                authenticated = True
                                dept_info = auth_result
                                response = {
                                    'status': 'success',
                                    'message': f"Welcome {auth_result['dept_name']}!",
                                    'dept_info': auth_result
                                }
                            else:
                                response = {
                                    'status': 'error',
                                    'message': auth_result.get('message', 'Authentication failed')
                                }

                        client_socket.send(json.dumps(response).encode('utf-8'))

                    elif action == 'submit_data' and authenticated:
                        entry_type = message.get('entry_type', '').strip()
                        data_content = message.get('data_content', '').strip()

                        if not entry_type or not data_content:
                            response = {
                                'status': 'error',
                                'message': 'Both category and content are required'
                            }
                        else:
                            # Save data with enhanced error handling
                            save_result = self.save_department_data(dept_info['dept_id'], entry_type, data_content)
                            
                            if save_result['success']:
                                response = {
                                    'status': 'success',
                                    'message': f'Data saved successfully! Entry ID: {save_result["entry_id"]}. CSV export completed for data analysis.',
                                    'entry_id': save_result['entry_id'],
                                    'dept_name': save_result.get('dept_name', 'Unknown')
                                }
                                self.log_activity(f"Data submission successful: {entry_type} by {dept_info['dept_name']}")
                            else:
                                response = {
                                    'status': 'error',
                                    'message': save_result['message']
                                }
                                self.log_activity(f"Data submission failed: {save_result['message']}")

                        client_socket.send(json.dumps(response).encode('utf-8'))

                    elif action == 'get_recent' and authenticated:
                        recent_entries = self.get_recent_entries()
                        response = {
                            'status': 'success',
                            'data': recent_entries
                        }
                        client_socket.send(json.dumps(response).encode('utf-8'))

                    elif action == 'export_csv' and authenticated:
                        filename = self.export_formatted_report()
                        if filename:
                            response = {
                                'status': 'success',
                                'message': f'Enhanced report exported to {filename}',
                                'filename': filename
                            }
                        else:
                            response = {
                                'status': 'error',
                                'message': 'Export failed'
                            }
                        client_socket.send(json.dumps(response).encode('utf-8'))

                    elif action == 'get_stats' and authenticated:
                        response = {
                            'status': 'success',
                            'stats': self.stats
                        }
                        client_socket.send(json.dumps(response).encode('utf-8'))

                    elif action == 'disconnect':
                        break

                    else:
                        response = {
                            'status': 'error',
                            'message': 'Invalid action or authentication required'
                        }
                        client_socket.send(json.dumps(response).encode('utf-8'))

                except json.JSONDecodeError as e:
                    response = {
                        'status': 'error',
                        'message': f'Invalid JSON format: {str(e)}'
                    }
                    client_socket.send(json.dumps(response).encode('utf-8'))

        except Exception as e:
            self.log_activity(f"Client handler error for {address}: {e}")

        finally:
            try:
                client_socket.close()
            except:
                pass

            if client_socket in self.clients:
                self.clients.remove(client_socket)

            self.log_activity(f"Connection with {address} closed")

    def start_server(self):
        """Start the server and listen for connections"""
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        try:
            server_socket.bind((self.host, self.port))
            server_socket.listen(5)
            self.running = True

            print("=" * 70)
            print("🚀 ENHANCED COLLEGE EXTENSION SERVER v2.0")
            print("=" * 70)
            print(f"📡 Server started on {self.host}:{self.port}")
            print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print("✨ Features:")
            print("   • Enhanced CSV export with analytics")
            print("   • Professional report generation")  
            print("   • Real-time activity monitoring")
            print("   • Advanced error handling")
            print("   • Connection timeout management")
            print("📋 Waiting for client connections...")
            print("=" * 70)

            while self.running:
                try:
                    client_socket, address = server_socket.accept()
                    self.clients.append(client_socket)

                    client_thread = threading.Thread(
                        target=self.handle_client,
                        args=(client_socket, address),
                        daemon=True
                    )
                    client_thread.start()

                except Exception as e:
                    if self.running:  # Only log if not shutting down
                        self.log_activity(f"Error accepting connection: {e}")

        except Exception as e:
            self.log_activity(f"Server error: {e}")

        finally:
            server_socket.close()
            self.log_activity("Server socket closed")

    def stop_server(self):
        """Stop the server gracefully"""
        self.running = False
        for client in self.clients:
            try:
                client.close()
            except:
                pass

if __name__ == "__main__":
    server = EnhancedCollegeServer()
    try:
        server.start_server()
    except KeyboardInterrupt:
        print("\n" + "=" * 70)
        print("🛑 SHUTTING DOWN SERVER...")
        print("=" * 70)
        print(f"📊 Final Statistics:")
        print(f"   • Total Connections: {server.stats['connections']}")
        print(f"   • Data Entries: {server.stats['data_entries']}")
        print(f"   • CSV Exports: {server.stats['exports']}")
        server.stop_server()
        print("✅ Server stopped successfully.")
        print("=" * 70)
