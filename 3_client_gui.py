"""
3_client_gui.py  (PATCHED 2025-08-16)

Enhanced College Extension – Client GUI
Fixes:
• Unlocks combobox / text area after successful login
• Robust socket receive – handles payloads >4 KB
• Better keyboard shortcuts and initial focus
• Cleaner logging + minor UI polish
• AUTO-CONNECTION: Automatically connects to server on startup
• HIDDEN CONNECTION: Server connection section is hidden
• FIXED DATA ENTRY: Data entry section works immediately after auto-connection
"""

import json
import socket
import tkinter as tk
from datetime import datetime
from tkinter import ttk, messagebox, scrolledtext
import threading
import time


class ModernCollegeClientGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Enhanced College Extension System - Department Portal")
        self.root.state("zoomed")

        # networking
        self.socket = None
        self.authenticated = False
        self.dept_info = None
        self.auto_connecting = False

        # colour palette - DARK MODE
        self.colors = {
            "primary": "#1a1a1a",           # Dark background
            "secondary": "#2d2d2d",          # Secondary dark
            "accent": "#4a9eff",            # Blue accent
            "success": "#4ade80",           # Green success
            "warning": "#fbbf24",           # Yellow warning
            "error": "#f87171",             # Red error
            "text": "#ffffff",              # White text
            "text_secondary": "#a1a1aa",    # Secondary text
            "light": "#374151",             # Light dark
            "white": "#1f1f1f",             # Card background
            "border": "#404040",            # Border color
            "input_bg": "#262626",          # Input background
            "input_text": "#ffffff",        # Input text
        }

        # build UI
        self.setup_modern_style()
        self.setup_gui()
        self.setup_keyboard_bindings()

        # start with e-mail field focused
        self.email_entry.focus_set()

        # auto-refresh handle
        self.refresh_timer = None
        
        # Auto-connect to server on startup
        self.root.after(1000, self.auto_connect_to_server)

    # --------------------------------------------------------------------- #
    #  STYLE                                                                
    # --------------------------------------------------------------------- #
    def setup_modern_style(self):
        style = ttk.Style()
        style.theme_use("clam")
        
        # Configure dark mode styles
        style.configure(
            "Title.TLabel",
            font=("Segoe UI", 24, "bold"),
            foreground=self.colors["text"],
            background=self.colors["primary"],
        )
        style.configure(
            "Heading.TLabel",
            font=("Segoe UI", 14, "bold"),
            foreground=self.colors["text"],
            background=self.colors["primary"],
        )
        style.configure(
            "Modern.TButton", 
            font=("Segoe UI", 10, "bold"), 
            padding=(20, 10),
            background=self.colors["accent"],
            foreground=self.colors["text"],
        )
        style.configure(
            "Success.TButton", 
            font=("Segoe UI", 11, "bold"), 
            padding=(25, 12),
            background=self.colors["success"],
            foreground=self.colors["text"],
        )
        style.map("Success.TButton", 
                 background=[("active", self.colors["success"])],
                 foreground=[("active", self.colors["text"])])
        style.configure(
            "Modern.TFrame", 
            background=self.colors["primary"], 
            relief="flat", 
            borderwidth=1
        )
        style.configure(
            "Card.TLabelFrame",
            background=self.colors["white"],
            relief="solid",
            borderwidth=1,
            foreground=self.colors["text"],
        )
        
        # Set root background to dark
        self.root.configure(bg=self.colors["primary"])

    # --------------------------------------------------------------------- #
    #  GUI LAYOUT                                                           
    # --------------------------------------------------------------------- #
    def setup_gui(self):
        main_container = tk.Frame(self.root, bg=self.colors["primary"])
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        self.setup_header(main_container)

        content_frame = tk.Frame(main_container, bg=self.colors["primary"])
        content_frame.pack(fill=tk.BOTH, expand=True, pady=(20, 0))

        left_panel = tk.Frame(content_frame, bg=self.colors["primary"])
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        right_panel = tk.Frame(content_frame, bg=self.colors["primary"])
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, padx=(10, 0))
        right_panel.configure(width=400)

        # REMOVED: self.setup_connection_section(left_panel) - Server connection section is hidden
        self.setup_login_section(left_panel)
        self.setup_data_entry_section(left_panel)

        self.setup_activity_panel(right_panel)
        self.setup_status_section(right_panel)
        
        # Add status bar at bottom
        self.setup_status_bar(main_container)

    # --------------------------------------------------------------------- #
    #  HEADER                                                               
    # --------------------------------------------------------------------- #
    def setup_header(self, parent):
        header_frame = tk.Frame(parent, bg=self.colors["secondary"], height=80)
        header_frame.pack(fill=tk.X, pady=(0, 20))
        header_frame.pack_propagate(False)

        title_frame = tk.Frame(header_frame, bg=self.colors["secondary"])
        title_frame.pack(expand=True)

        tk.Label(
            title_frame,
            text="College Extension System",
            font=("Segoe UI", 24, "bold"),
            fg=self.colors["text"],
            bg=self.colors["secondary"],
        ).pack(pady=(15, 0))

        tk.Label(
            title_frame,
            text="Department Portal",
            font=("Segoe UI", 12),
            fg=self.colors["text_secondary"],
            bg=self.colors["secondary"],
        ).pack()

        self.connection_status = tk.Label(
            header_frame,
            text="● Connecting...",
            font=("Segoe UI", 10, "bold"),
            fg=self.colors["warning"],
            bg=self.colors["secondary"],
        )
        self.connection_status.place(relx=1.0, y=10, anchor="ne", x=-20)

    # --------------------------------------------------------------------- #
    #  AUTO-CONNECTION TO SERVER                                            
    # --------------------------------------------------------------------- #
    def auto_connect_to_server(self):
        """Automatically connect to server on startup"""
        if self.auto_connecting:
            return
            
        self.auto_connecting = True
        self.log("Auto-connecting to server...", "INFO")
        
        # Try to connect in a separate thread to avoid blocking UI
        def connect_thread():
            try:
                # Default server settings
                server_ip = "localhost"
                server_port = 9999
                
                self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.socket.connect((server_ip, server_port))
                
                # Update UI on main thread
                self.root.after(0, self.on_auto_connect_success, server_ip, server_port)
                
            except Exception as e:
                # Update UI on main thread
                self.root.after(0, self.on_auto_connect_failed, str(e))
        
        threading.Thread(target=connect_thread, daemon=True).start()
    
    def on_auto_connect_success(self, server_ip, server_port):
        """Handle successful auto-connection"""
        self.auto_connecting = False
        self.log(f"Auto-connected to {server_ip}:{server_port}", "SUCCESS")
        self.update_connection_status(True)
        self.login_btn.config(state=tk.NORMAL)
        self.log("✓ Server connection established", "SUCCESS")
        
        # Enable data entry fields immediately after connection
        self.enable_data_entry()
    
    def on_auto_connect_failed(self, error_msg):
        """Handle failed auto-connection"""
        self.auto_connecting = False
        self.log(f"Auto-connection failed: {error_msg}", "ERROR")
        self.update_connection_status(False)
        
        # Retry connection after 5 seconds
        self.root.after(5000, self.auto_connect_to_server)

    # --------------------------------------------------------------------- #
    #  LOGIN SECTION                                                        
    # --------------------------------------------------------------------- #
    def setup_login_section(self, parent):
        login_card = tk.LabelFrame(
            parent,
            text=" Department Authentication ",
            font=("Segoe UI", 12, "bold"),
            fg=self.colors["text"],
            bg=self.colors["white"],
            padx=20,
            pady=15,
            relief="solid",
            borderwidth=1,
        )
        login_card.pack(fill=tk.X, pady=(0, 15))

        form_frame = tk.Frame(login_card, bg=self.colors["white"])
        form_frame.pack(fill=tk.X)

        # EMAIL
        tk.Label(
            form_frame,
            text="Department Email:",
            font=("Segoe UI", 12, "bold"),
            bg=self.colors["white"],
            fg=self.colors["text"],
        ).pack(anchor="w")
        self.email_var = tk.StringVar()
        self.email_entry = tk.Entry(
            form_frame,
            textvariable=self.email_var,
            font=("Segoe UI", 12),
            relief="solid",
            borderwidth=1,
            bg=self.colors["input_bg"],
            fg=self.colors["input_text"],
            insertbackground=self.colors["text"],
        )
        self.email_entry.pack(anchor="w", pady=(5, 10), fill=tk.X)

        # PASSWORD
        tk.Label(
            form_frame,
            text="Password:",
            font=("Segoe UI", 12, "bold"),
            bg=self.colors["white"],
            fg=self.colors["text"],
        ).pack(anchor="w")
        self.password_var = tk.StringVar()
        self.password_entry = tk.Entry(
            form_frame,
            textvariable=self.password_var,
            font=("Segoe UI", 12),
            relief="solid",
            borderwidth=1,
            show="*",
            bg=self.colors["input_bg"],
            fg=self.colors["input_text"],
            insertbackground=self.colors["text"],
        )
        self.password_entry.pack(anchor="w", pady=(5, 10), fill=tk.X)

        # LOGIN BUTTON
        self.login_btn = tk.Button(
            form_frame,
            text="Login",
            command=self.login,
            bg=self.colors["success"],
            fg=self.colors["text"],
            font=("Segoe UI", 12, "bold"),
            relief="flat",
            cursor="hand2",
            state=tk.DISABLED,  # Will be enabled after auto-connection
        )
        self.login_btn.pack(side=tk.LEFT, pady=10)

        # sample creds
        sample_frame = tk.Frame(
            login_card, bg=self.colors["secondary"], relief="solid", borderwidth=1
        )
        sample_frame.pack(fill=tk.X, pady=10)
        tk.Label(
            sample_frame,
            text="Sample Credentials:",
            font=("Segoe UI", 11, "bold"),
            bg=self.colors["secondary"],
            fg=self.colors["text"],
        ).pack(anchor="w", padx=10, pady=5)
        tk.Label(
            sample_frame,
            text="Email: cs@college.edu",
            font=("Segoe UI", 10),
            bg=self.colors["secondary"],
            fg=self.colors["text_secondary"],
        ).pack(anchor="w", padx=10)
        tk.Label(
            sample_frame,
            text="Password: cs_password123",
            font=("Segoe UI", 10),
            bg=self.colors["secondary"],
            fg=self.colors["text_secondary"],
        ).pack(anchor="w", padx=10)

    # --------------------------------------------------------------------- #
    #  DATA ENTRY SECTION                                                   
    # --------------------------------------------------------------------- #
    def setup_data_entry_section(self, parent):
        data_card = tk.LabelFrame(
            parent,
            text=" Data Entry & Submission ",
            font=("Segoe UI", 12, "bold"),
            fg=self.colors["text"],
            bg=self.colors["white"],
            padx=20,
            pady=15,
            relief="solid",
            borderwidth=1,
        )
        data_card.pack(fill=tk.BOTH, expand=True)

        # CATEGORY
        tk.Label(
            data_card,
            text="Entry Category:",
            font=("Segoe UI", 12, "bold"),
            bg=self.colors["white"],
            fg=self.colors["text"],
        ).pack(anchor="w")

        self.entry_type = tk.StringVar()
        self.entry_combo = ttk.Combobox(
            data_card,
            textvariable=self.entry_type,
            values=[
                "Student Records",
                "Faculty Data",
                "Course Information",
                "Research Data",
                "Administrative Info",
                "Other",
            ],
            state="disabled",  # Will be enabled after auto-connection
            font=("Segoe UI", 12),
        )
        self.entry_combo.pack(anchor="w", pady=(5, 15), fill=tk.X)
        
        # Style the combobox for dark mode
        style = ttk.Style()
        style.map('TCombobox',
            fieldbackground=[('readonly', self.colors["input_bg"])],
            background=[('readonly', self.colors["input_bg"])],
            foreground=[('readonly', self.colors["input_text"])],
            selectbackground=[('readonly', self.colors["accent"])],
            selectforeground=[('readonly', self.colors["text"])]
        )

        # CONTENT
        tk.Label(
            data_card,
            text="Data Content:",
            font=("Segoe UI", 12, "bold"),
            bg=self.colors["white"],
            fg=self.colors["text"],
        ).pack(anchor="w")
        
        # Add helpful instruction
        instruction_label = tk.Label(
            data_card,
            text="💡 Tip: Use Ctrl+Enter to quickly submit your data entry",
            font=("Segoe UI", 9),
            bg=self.colors["white"],
            fg=self.colors["text_secondary"],
        )
        instruction_label.pack(anchor="w", pady=(0, 5))

        text_frame = tk.Frame(data_card, bg=self.colors["white"])
        text_frame.pack(fill=tk.BOTH, expand=True, pady=(5, 15))

        self.data_content = scrolledtext.ScrolledText(
            text_frame,
            wrap=tk.WORD,
            font=("Segoe UI", 11),
            relief="solid",
            borderwidth=1,
            state=tk.DISABLED,  # Will be enabled after auto-connection
            bg=self.colors["input_bg"],
            fg=self.colors["input_text"],
            insertbackground=self.colors["text"],
        )
        self.data_content.pack(fill=tk.BOTH, expand=True)

        # BUTTONS
        btn_frame = tk.Frame(data_card, bg=self.colors["white"])
        btn_frame.pack(fill=tk.X, pady=(10, 0))

        self.submit_btn = tk.Button(
            btn_frame,
            text="Save Data",
            command=self.submit_data,
            bg=self.colors["success"],
            fg=self.colors["text"],
            font=("Segoe UI", 12, "bold"),
            relief="flat",
            cursor="hand2",
            state=tk.DISABLED,  # Will be enabled after auto-connection
        )
        self.submit_btn.pack(side=tk.LEFT, padx=(0, 10))

        self.export_btn = tk.Button(
            btn_frame,
            text="Export CSV",
            command=self.export_csv,
            bg=self.colors["accent"],
            fg=self.colors["text"],
            font=("Segoe UI", 12, "bold"),
            relief="flat",
            cursor="hand2",
            state=tk.DISABLED,  # Will be enabled after auto-connection
        )
        self.export_btn.pack(side=tk.LEFT, padx=(0, 10))

        self.clear_btn = tk.Button(
            btn_frame,
            text="Clear",
            command=self.clear_data,
            bg=self.colors["secondary"],
            fg=self.colors["text"],
            font=("Segoe UI", 12, "bold"),
            relief="flat",
            cursor="hand2",
            state=tk.DISABLED,  # Will be enabled after auto-connection
        )
        self.clear_btn.pack(side=tk.LEFT)

    # --------------------------------------------------------------------- #
    #  RIGHT-PANEL: ACTIVITY + STATUS                                       
    # --------------------------------------------------------------------- #
    def setup_activity_panel(self, parent):
        activity_card = tk.LabelFrame(
            parent,
            text=" Recent Activity ",
            font=("Segoe UI", 12, "bold"),
            fg=self.colors["text"],
            bg=self.colors["white"],
            padx=10,
            pady=10,
            relief="solid",
            borderwidth=1,
        )
        activity_card.pack(fill=tk.BOTH, expand=True)

        self.activity_listbox = tk.Listbox(
            activity_card, 
            font=("Segoe UI", 11), 
            selectmode=tk.SINGLE,
            bg=self.colors["input_bg"],
            fg=self.colors["input_text"],
            selectbackground=self.colors["accent"],
            selectforeground=self.colors["text"],
        )
        self.activity_listbox.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        tk.Button(
            activity_card,
            text="Refresh",
            command=self.refresh_activity,
            bg=self.colors["accent"],
            fg=self.colors["text"],
            font=("Segoe UI", 11, "bold"),
            relief="flat",
            cursor="hand2",
        ).pack(anchor="e")

    def setup_status_section(self, parent):
        status_card = tk.LabelFrame(
            parent,
            text=" System Status ",
            font=("Segoe UI", 12, "bold"),
            fg=self.colors["text"],
            bg=self.colors["white"],
            padx=10,
            pady=10,
            relief="solid",
            borderwidth=1,
        )
        status_card.pack(fill=tk.BOTH, expand=True)

        self.status_text = scrolledtext.ScrolledText(
            status_card, 
            font=("Consolas", 10), 
            wrap=tk.WORD, 
            state=tk.DISABLED,
            bg=self.colors["input_bg"],
            fg=self.colors["input_text"],
            insertbackground=self.colors["text"],
        )
        self.status_text.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        tk.Button(
            status_card,
            text="Clear Log",
            command=self.clear_status,
            bg=self.colors["secondary"],
            fg=self.colors["text"],
            font=("Segoe UI", 11, "bold"),
            relief="flat",
            cursor="hand2",
        ).pack(anchor="e")

    # --------------------------------------------------------------------- #
    #  STATUS BAR                                                           
    # --------------------------------------------------------------------- #
    def setup_status_bar(self, parent):
        """Add status bar at bottom of application"""
        status_frame = tk.Frame(parent, bg=self.colors["secondary"], height=30)
        status_frame.pack(fill=tk.X, side=tk.BOTTOM, pady=(10, 0))
        status_frame.pack_propagate(False)
        
        # Status information
        self.status_label = tk.Label(
            status_frame,
            text="Ready - Auto-connecting to server...",
            font=("Segoe UI", 9),
            fg=self.colors["text_secondary"],
            bg=self.colors["secondary"],
        )
        self.status_label.pack(side=tk.LEFT, padx=10, pady=5)
        
        # Department info (shown after login)
        self.dept_status_label = tk.Label(
            status_frame,
            text="",
            font=("Segoe UI", 9, "bold"),
            fg=self.colors["accent"],
            bg=self.colors["secondary"],
        )
        self.dept_status_label.pack(side=tk.RIGHT, padx=10, pady=5)

    # --------------------------------------------------------------------- #
    #  KEYBOARD SHORTCUTS                                                   
    # --------------------------------------------------------------------- #
    def setup_keyboard_bindings(self):
        # Submit – Ctrl+S and Ctrl+Enter
        self.root.bind("<Control-s>", lambda _: self.submit_data() if self.authenticated else None)
        self.root.bind("<Control-Return>", lambda _: self.submit_data() if self.authenticated else None)
        self.root.bind("<Control-Key-Return>", lambda _: self.submit_data() if self.authenticated else None)
        
        # Refresh – F5
        self.root.bind("<F5>", lambda _: self.refresh_activity())
        
        # Esc – clear
        self.root.bind("<Escape>", lambda _: self.clear_data())
        
        # Enter key navigation
        self.email_entry.bind("<Return>", lambda _: self.password_entry.focus_set())
        self.password_entry.bind("<Return>", lambda _: self.login())
        
        # Data entry shortcuts
        self.data_content.bind("<Control-Return>", lambda _: self.submit_data() if self.authenticated else None)
        self.data_content.bind("<Control-Key-Return>", lambda _: self.submit_data() if self.authenticated else None)
        
        # Focus management
        self.entry_combo.bind("<Return>", lambda _: self.data_content.focus_set())
        self.data_content.bind("<Tab>", lambda _: self.submit_btn.focus_set())

    # --------------------------------------------------------------------- #
    #  LOGGING                                                              
    # --------------------------------------------------------------------- #
    def log(self, message, level="INFO"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        msg = f"[{timestamp}] {level}: {message}\n"
        self.status_text.configure(state=tk.NORMAL)
        self.status_text.insert(tk.END, msg)
        self.status_text.see(tk.END)
        self.status_text.configure(state=tk.DISABLED)
        self.root.update_idletasks()

    def clear_status(self):
        self.status_text.configure(state=tk.NORMAL)
        self.status_text.delete(1.0, tk.END)
        self.status_text.configure(state=tk.DISABLED)

    # --------------------------------------------------------------------- #
    #  CONNECTION HANDLERS                                                  
    # --------------------------------------------------------------------- #
    def update_connection_status(self, connected, dept_name=None):
        if connected:
            text = "● Connected"
            if dept_name:
                text += f" ({dept_name})"
            self.connection_status.config(text=text, fg=self.colors["success"])
            self.status_label.config(text="Connected to server - Ready for data entry")
        else:
            self.connection_status.config(text="● Disconnected", fg=self.colors["error"])
            self.status_label.config(text="Disconnected from server - Attempting to reconnect...")

    def update_dept_status(self, dept_name):
        """Update department status in status bar"""
        if dept_name:
            self.dept_status_label.config(text=f"Department: {dept_name}")
        else:
            self.dept_status_label.config(text="")

    def disconnect_from_server(self):
        """Disconnect from server and reset UI"""
        try:
            if self.socket:
                self.socket.send(json.dumps({"action": "disconnect"}).encode())
                self.socket.close()
        except Exception:
            pass

        self.socket = None
        self.authenticated = False
        self.dept_info = None
        self.log("Disconnected from server.", "INFO")
        self.update_connection_status(False)
        self.update_dept_status("")

        # reset UI
        self.login_btn.config(state=tk.DISABLED)
        self.submit_btn.config(state=tk.DISABLED)
        self.export_btn.config(state=tk.DISABLED)
        self.clear_btn.config(state=tk.DISABLED)
        self.entry_combo.configure(state="disabled")
        self.data_content.configure(state=tk.DISABLED, bg=self.colors["input_bg"], fg=self.colors["input_text"])
        
        # Try to reconnect after a delay
        self.root.after(3000, self.auto_connect_to_server)

    # --------------------------------------------------------------------- #
    #  ENABLE DATA ENTRY POST-LOGIN                                         
    # --------------------------------------------------------------------- #
    def enable_data_entry(self):
        self.entry_combo.configure(state="normal")
        self.data_content.configure(state=tk.NORMAL, bg=self.colors["input_bg"], fg=self.colors["input_text"])
        self.submit_btn.config(state=tk.NORMAL)
        self.export_btn.config(state=tk.NORMAL)
        self.clear_btn.config(state=tk.NORMAL)
        self.entry_combo.focus_set()
        self.root.update_idletasks()

    # --------------------------------------------------------------------- #
    #  LOGIN                                                                
    # --------------------------------------------------------------------- #
    def login(self):
        """Authenticate department user with enhanced validation and error handling"""
        if not self.socket:
            messagebox.showerror("Connection Error", "Server connection not available. Please wait for auto-connection or restart the application.")
            return

        # Get and validate credentials
        email = self.email_var.get().strip()
        password = self.password_var.get().strip()
        
        if not email:
            messagebox.showerror("Input Error", "Please enter your department email address.")
            self.email_entry.focus_set()
            return
            
        if not password:
            messagebox.showerror("Input Error", "Please enter your password.")
            self.password_entry.focus_set()
            return

        # Show login in progress
        self.log(f"Attempting login for: {email}", "INFO")
        self.login_btn.config(state=tk.DISABLED, text="Logging in...")
        self.root.update_idletasks()

        try:
            # Prepare login data
            login_data = {
                "action": "login", 
                "email": email, 
                "password": password
            }
            
            # Send login request
            self.socket.send(json.dumps(login_data).encode())

            # Receive response with robust handling
            response_data = b""
            while True:
                chunk = self.socket.recv(4096)
                if not chunk:
                    break
                response_data += chunk
                try:
                    res_data = json.loads(response_data.decode())
                    break
                except json.JSONDecodeError:
                    continue

            # Process login response
            if res_data.get("status") == "success":
                self.authenticated = True
                self.dept_info = res_data.get("dept_info")
                
                # Update UI
                dept_name = self.dept_info.get("dept_name", "Unknown Department")
                self.log(f"Login successful: {dept_name}", "SUCCESS")
                self.update_connection_status(True, dept_name)
                self.update_dept_status(dept_name)
                self.login_btn.config(state=tk.DISABLED)
                self.password_var.set("")
                
                # Enable data entry and start auto-refresh
                self.enable_data_entry()
                self.start_auto_refresh()
                
                # Show success message
                messagebox.showinfo("Login Successful", f"Welcome {dept_name}!\n\nYou can now enter data and it will be automatically exported as CSV for analysis.")
                self.log("✓ Data entry system enabled", "SUCCESS")
                
            else:
                error_msg = res_data.get("message", "Authentication failed")
                messagebox.showerror("Login Failed", f"Login failed:\n\n{error_msg}")
                self.log(f"Login failed: {error_msg}", "ERROR")
                self.password_var.set("")
                self.password_entry.focus_set()
                
        except json.JSONDecodeError as e:
            messagebox.showerror("Communication Error", "Invalid response from server. Please try again.")
            self.log(f"JSON decode error during login: {e}", "ERROR")
            
        except Exception as e:
            messagebox.showerror("Login Error", f"An error occurred during login:\n\n{str(e)}")
            self.log(f"Login error: {e}", "ERROR")
            
        finally:
            # Restore button state
            self.login_btn.config(state=tk.NORMAL, text="Login")
            self.root.update_idletasks()

    # --------------------------------------------------------------------- #
    #  DATA SUBMISSION                                                      
    # --------------------------------------------------------------------- #
    def submit_data(self):
        """Submit data entry to server with enhanced validation and error handling"""
        if not self.authenticated:
            messagebox.showerror("Authentication Error", "Please login first to submit data.")
            return

        # Get and validate input
        category = self.entry_type.get().strip()
        content = self.data_content.get(1.0, tk.END).strip()
        
        # Enhanced validation
        if not category:
            messagebox.showerror("Input Error", "Please select a category for your data entry.")
            self.entry_combo.focus_set()
            return
            
        if not content:
            messagebox.showerror("Input Error", "Please enter data content before submitting.")
            self.data_content.focus_set()
            return
            
        if len(content) < 10:
            messagebox.showerror("Input Error", "Data content must be at least 10 characters long.")
            self.data_content.focus_set()
            return
            
        if len(content) > 10000:
            messagebox.showerror("Input Error", "Data content is too long. Maximum 10,000 characters allowed.")
            self.data_content.focus_set()
            return

        # Show submission in progress
        self.log(f"Submitting data: {category}", "INFO")
        self.status_label.config(text=f"Submitting data: {category}...")
        self.submit_btn.config(state=tk.DISABLED, text="Submitting...")
        self.root.update_idletasks()

        try:
            # Prepare submission data
            submission_data = {
                "action": "submit_data", 
                "entry_type": category, 
                "data_content": content
            }
            
            # Send data to server
            self.socket.send(json.dumps(submission_data).encode())
            
            # Receive response with robust handling
            response_data = b""
            while True:
                chunk = self.socket.recv(4096)
                if not chunk:
                    break
                response_data += chunk
                try:
                    res_data = json.loads(response_data.decode())
                    break
                except json.JSONDecodeError:
                    continue

            # Process response
            if res_data.get("status") == "success":
                self.log(f"Data submitted successfully: {category}", "SUCCESS")
                self.status_label.config(text=f"Data saved successfully! CSV exported for analysis.")
                messagebox.showinfo("Success", "Data saved successfully!\n\nCSV export has been automatically generated for data analysis.")
                
                # Clear form and refresh
                self.clear_data()
                self.refresh_activity()
                
                # Show success feedback
                self.log("✓ Data entry completed and CSV exported", "SUCCESS")
                
            else:
                error_msg = res_data.get("message", "Unknown error occurred")
                self.status_label.config(text=f"Submission failed: {error_msg}")
                messagebox.showerror("Submission Failed", f"Failed to save data:\n\n{error_msg}")
                self.log(f"Data submission failed: {error_msg}", "ERROR")
                
        except json.JSONDecodeError as e:
            messagebox.showerror("Communication Error", "Invalid response from server. Please try again.")
            self.log(f"JSON decode error: {e}", "ERROR")
            
        except Exception as e:
            messagebox.showerror("Submission Error", f"An error occurred while submitting data:\n\n{str(e)}")
            self.log(f"Data submission error: {e}", "ERROR")
            
        finally:
            # Restore button state and status
            self.submit_btn.config(state=tk.NORMAL, text="Save Data")
            if self.authenticated:
                self.status_label.config(text="Ready for data entry")
            self.root.update_idletasks()

    # --------------------------------------------------------------------- #
    #  EXPORT CSV                                                           
    # --------------------------------------------------------------------- #
    def export_csv(self):
        if not self.authenticated:
            messagebox.showerror("Error", "Login required to export data.")
            return

        try:
            self.socket.send(json.dumps({"action": "export_csv"}).encode())
            res_data = json.loads(self.socket.recv(4096).decode())
            if res_data.get("status") == "success":
                self.log(f"CSV exported: {res_data.get('filename')}", "SUCCESS")
                messagebox.showinfo(
                    "Export Success", f"Data exported to {res_data.get('filename')}"
                )
            else:
                messagebox.showerror("Export Failed", res_data.get("message"))
                self.log(f"Export failed: {res_data.get('message')}", "ERROR")
        except Exception as e:
            messagebox.showerror("Error", f"Export error: {e}")
            self.log(f"Export error: {e}", "ERROR")

    # --------------------------------------------------------------------- #
    #  RECENT ACTIVITY                                                      
    # --------------------------------------------------------------------- #
    def refresh_activity(self):
        if not self.authenticated:
            return
        try:
            self.socket.send(json.dumps({"action": "get_recent"}).encode())
            res_data = json.loads(self.socket.recv(4096).decode())
            if res_data.get("status") == "success":
                self.activity_listbox.delete(0, tk.END)
                for entry in res_data.get("data", []):
                    time_str = entry.get("created_at", "")[:16]
                    display_text = f"{time_str} - {entry.get('dept_name', '')}: {entry.get('entry_type', '')}"
                    self.activity_listbox.insert(tk.END, display_text)
        except Exception as e:
            self.log(f"Refresh error: {e}", "WARNING")

    def start_auto_refresh(self):
        if self.authenticated:
            self.refresh_activity()
            self.refresh_timer = self.root.after(30_000, self.start_auto_refresh)

    # --------------------------------------------------------------------- #
    #  MISC HELPERS                                                         
    # --------------------------------------------------------------------- #
    def clear_data(self):
        if self.authenticated:
            self.entry_type.set("")
            self.data_content.delete(1.0, tk.END)
            self.entry_combo.focus_set()

    def on_closing(self):
        if self.refresh_timer:
            self.root.after_cancel(self.refresh_timer)
        if self.socket:
            self.disconnect_from_server()
        self.root.destroy()


# ------------------------------------------------------------------------- #
#  MAIN ENTRY                                                              
# ------------------------------------------------------------------------- #
def main():
    root = tk.Tk()
    app = ModernCollegeClientGUI(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()


if __name__ == "__main__":
    main()
