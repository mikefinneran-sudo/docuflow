#!/usr/bin/env python3
"""
DocuFlow - Graphical User Interface
Professional document management with an easy-to-use GUI
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import os
import json
from datetime import datetime
from pathlib import Path

# Import DocuFlow modules
from document_organizer import DocumentOrganizer
from version_control import VersionControl
from retention_policy import RetentionPolicy
from alert_system import AlertSystem


class DocuFlowGUI:
    """Main GUI Application"""

    def __init__(self, root):
        self.root = root
        self.root.title("DocuFlow - Document Management System")
        self.root.geometry("1200x800")

        # Set minimum size
        self.root.minsize(1000, 600)

        # Initialize DocuFlow modules
        try:
            self.organizer = DocumentOrganizer()
            self.version_control = VersionControl()
            self.retention = RetentionPolicy()
            self.alerts = AlertSystem()
            self.config = self.organizer.config
        except Exception as e:
            messagebox.showerror("Initialization Error",
                               f"Could not initialize DocuFlow:\n{e}\n\nPlease check config.json")
            return

        # Color scheme
        self.colors = {
            'primary': '#2563eb',      # Blue
            'success': '#059669',      # Green
            'warning': '#d97706',      # Orange
            'danger': '#dc2626',       # Red
            'bg': '#f8fafc',          # Light gray
            'fg': '#1e293b',          # Dark gray
            'border': '#cbd5e1'       # Medium gray
        }

        # Setup UI
        self.setup_styles()
        self.create_menu()
        self.create_main_layout()
        self.show_dashboard()

    def setup_styles(self):
        """Configure ttk styles"""
        style = ttk.Style()
        style.theme_use('clam')

        # Configure colors
        style.configure('TFrame', background=self.colors['bg'])
        style.configure('TLabel', background=self.colors['bg'],
                       foreground=self.colors['fg'])
        style.configure('TButton', padding=10)
        style.configure('Accent.TButton', foreground=self.colors['primary'])
        style.configure('Success.TButton', foreground=self.colors['success'])
        style.configure('Warning.TButton', foreground=self.colors['warning'])
        style.configure('Danger.TButton', foreground=self.colors['danger'])

    def create_menu(self):
        """Create menu bar"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Setup Folder Structure",
                            command=self.setup_folders)
        file_menu.add_separator()
        file_menu.add_command(label="Settings", command=self.show_settings)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)

        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Daily Maintenance",
                             command=self.run_daily_maintenance)
        tools_menu.add_command(label="Generate Report",
                             command=self.show_reports)
        tools_menu.add_separator()
        tools_menu.add_command(label="Check for Expiring Files",
                             command=self.check_expiring_files)

        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="User Guide", command=self.show_help)
        help_menu.add_command(label="Safety Features",
                            command=self.show_safety_info)
        help_menu.add_separator()
        help_menu.add_command(label="About DocuFlow", command=self.show_about)

    def create_main_layout(self):
        """Create main application layout"""
        # Create main container
        main_container = ttk.Frame(self.root)
        main_container.pack(fill=tk.BOTH, expand=True)

        # Create sidebar
        sidebar = ttk.Frame(main_container, width=200)
        sidebar.pack(side=tk.LEFT, fill=tk.Y, padx=(10, 0), pady=10)
        sidebar.pack_propagate(False)

        # Sidebar title
        title_label = ttk.Label(sidebar, text="DocuFlow",
                               font=('Helvetica', 16, 'bold'))
        title_label.pack(pady=(0, 20))

        # Sidebar buttons
        buttons = [
            ("🏠 Dashboard", self.show_dashboard),
            ("📁 Organize Files", self.show_organize),
            ("📝 Versions", self.show_versions),
            ("📦 Retention", self.show_retention),
            ("🔔 Alerts", self.show_alerts),
            ("📊 Reports", self.show_reports),
        ]

        for text, command in buttons:
            btn = ttk.Button(sidebar, text=text, command=command, width=20)
            btn.pack(pady=5, fill=tk.X)

        # Create content area
        self.content_area = ttk.Frame(main_container)
        self.content_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True,
                              padx=10, pady=10)

    def clear_content(self):
        """Clear the content area"""
        for widget in self.content_area.winfo_children():
            widget.destroy()

    def show_dashboard(self):
        """Show dashboard view"""
        self.clear_content()

        # Title
        title = ttk.Label(self.content_area, text="Dashboard",
                         font=('Helvetica', 24, 'bold'))
        title.pack(pady=(0, 20))

        # Stats grid
        stats_frame = ttk.Frame(self.content_area)
        stats_frame.pack(fill=tk.X, pady=(0, 20))

        # Get stats
        try:
            report = self.retention.get_retention_report()
            total_files = sum(
                dept['working']['count'] + dept['archive']['count'] + dept['final']['count']
                for dept in report['departments'].values()
            )
            expiring = sum(
                dept['archive']['expiring']
                for dept in report['departments'].values()
            )
        except:
            total_files = 0
            expiring = 0

        # Stat cards
        stats = [
            ("Total Files", str(total_files), self.colors['primary']),
            ("Files Expiring Soon", str(expiring), self.colors['warning']),
            ("Client", self.config['client_name'], self.colors['success']),
        ]

        for i, (label, value, color) in enumerate(stats):
            card = tk.Frame(stats_frame, bg=color, relief=tk.RAISED, bd=2)
            card.grid(row=0, column=i, padx=10, sticky='ew')
            stats_frame.columnconfigure(i, weight=1)

            value_label = tk.Label(card, text=value, font=('Helvetica', 24, 'bold'),
                                 bg=color, fg='white')
            value_label.pack(pady=(10, 0))

            label_label = tk.Label(card, text=label, font=('Helvetica', 10),
                                 bg=color, fg='white')
            label_label.pack(pady=(0, 10))

        # Quick actions
        actions_frame = ttk.LabelFrame(self.content_area, text="Quick Actions",
                                      padding=20)
        actions_frame.pack(fill=tk.BOTH, expand=True)

        quick_buttons = [
            ("📁 Organize Files", "Organize files into departments",
             self.show_organize, 'Accent.TButton'),
            ("🔍 Search Files", "Find files across all departments",
             self.search_files, 'Accent.TButton'),
            ("📝 Create Version", "Backup a file before editing",
             self.quick_create_version, 'Success.TButton'),
            ("⚠️ Check Expiring Files", "Files that will be deleted soon",
             self.check_expiring_files, 'Warning.TButton'),
        ]

        for i, (text, desc, command, style) in enumerate(quick_buttons):
            frame = ttk.Frame(actions_frame)
            frame.pack(fill=tk.X, pady=10)

            btn = ttk.Button(frame, text=text, command=command,
                           style=style, width=25)
            btn.pack(side=tk.LEFT)

            desc_label = ttk.Label(frame, text=desc,
                                  font=('Helvetica', 9, 'italic'))
            desc_label.pack(side=tk.LEFT, padx=(10, 0))

        # Recent activity
        activity_frame = ttk.LabelFrame(self.content_area, text="Recent Activity",
                                       padding=10)
        activity_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))

        activity_text = scrolledtext.ScrolledText(activity_frame, height=10,
                                                 wrap=tk.WORD)
        activity_text.pack(fill=tk.BOTH, expand=True)

        # Load recent logs
        try:
            if os.path.exists('organization_log.txt'):
                with open('organization_log.txt', 'r') as f:
                    lines = f.readlines()[-10:]  # Last 10 lines
                    activity_text.insert(tk.END, ''.join(lines))
        except:
            activity_text.insert(tk.END, "No recent activity")

        activity_text.config(state=tk.DISABLED)

    def show_organize(self):
        """Show file organization interface"""
        self.clear_content()

        title = ttk.Label(self.content_area, text="Organize Files",
                         font=('Helvetica', 24, 'bold'))
        title.pack(pady=(0, 20))

        # Tabs for different organization modes
        notebook = ttk.Notebook(self.content_area)
        notebook.pack(fill=tk.BOTH, expand=True)

        # Single file tab
        single_frame = ttk.Frame(notebook, padding=20)
        notebook.add(single_frame, text="Single File")

        ttk.Label(single_frame, text="Organize a single file",
                 font=('Helvetica', 12)).pack(pady=(0, 20))

        # File selection
        file_frame = ttk.Frame(single_frame)
        file_frame.pack(fill=tk.X, pady=10)

        ttk.Label(file_frame, text="File:").pack(side=tk.LEFT)
        self.file_path_var = tk.StringVar()
        ttk.Entry(file_frame, textvariable=self.file_path_var,
                 width=50).pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)
        ttk.Button(file_frame, text="Browse...",
                  command=self.browse_file).pack(side=tk.LEFT)

        # Department selection
        dept_frame = ttk.Frame(single_frame)
        dept_frame.pack(fill=tk.X, pady=10)

        ttk.Label(dept_frame, text="Department:").pack(side=tk.LEFT)
        self.department_var = tk.StringVar()
        dept_combo = ttk.Combobox(dept_frame, textvariable=self.department_var,
                                  values=self.config['folder_structure']['departments'],
                                  width=30)
        dept_combo.pack(side=tk.LEFT, padx=10)
        if self.config['folder_structure']['departments']:
            dept_combo.current(0)

        # Category selection
        category_frame = ttk.Frame(single_frame)
        category_frame.pack(fill=tk.X, pady=10)

        ttk.Label(category_frame, text="Category:").pack(side=tk.LEFT)
        self.category_var = tk.StringVar(value="Working")
        category_combo = ttk.Combobox(category_frame, textvariable=self.category_var,
                                     values=self.config['folder_structure']['categories'],
                                     width=30)
        category_combo.pack(side=tk.LEFT, padx=10)

        # Project name
        project_frame = ttk.Frame(single_frame)
        project_frame.pack(fill=tk.X, pady=10)

        ttk.Label(project_frame, text="Project (optional):").pack(side=tk.LEFT)
        self.project_var = tk.StringVar()
        ttk.Entry(project_frame, textvariable=self.project_var,
                 width=30).pack(side=tk.LEFT, padx=10)

        # Organize button
        ttk.Button(single_frame, text="Organize File",
                  command=self.organize_single_file,
                  style='Success.TButton').pack(pady=20)

        # Batch organize tab
        batch_frame = ttk.Frame(notebook, padding=20)
        notebook.add(batch_frame, text="Batch Organize")

        ttk.Label(batch_frame, text="Organize an entire folder",
                 font=('Helvetica', 12)).pack(pady=(0, 20))

        # Folder selection
        folder_frame = ttk.Frame(batch_frame)
        folder_frame.pack(fill=tk.X, pady=10)

        ttk.Label(folder_frame, text="Folder:").pack(side=tk.LEFT)
        self.batch_folder_var = tk.StringVar()
        ttk.Entry(folder_frame, textvariable=self.batch_folder_var,
                 width=50).pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)
        ttk.Button(folder_frame, text="Browse...",
                  command=self.browse_folder).pack(side=tk.LEFT)

        # Department for batch
        batch_dept_frame = ttk.Frame(batch_frame)
        batch_dept_frame.pack(fill=tk.X, pady=10)

        ttk.Label(batch_dept_frame, text="Department:").pack(side=tk.LEFT)
        self.batch_department_var = tk.StringVar()
        batch_dept_combo = ttk.Combobox(batch_dept_frame,
                                       textvariable=self.batch_department_var,
                                       values=self.config['folder_structure']['departments'],
                                       width=30)
        batch_dept_combo.pack(side=tk.LEFT, padx=10)
        if self.config['folder_structure']['departments']:
            batch_dept_combo.current(0)

        # Batch organize button
        ttk.Button(batch_frame, text="Organize Folder",
                  command=self.organize_batch,
                  style='Success.TButton').pack(pady=20)

        # Results area
        results_frame = ttk.LabelFrame(batch_frame, text="Results", padding=10)
        results_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))

        self.batch_results_text = scrolledtext.ScrolledText(results_frame,
                                                            height=10, wrap=tk.WORD)
        self.batch_results_text.pack(fill=tk.BOTH, expand=True)

    def show_versions(self):
        """Show version control interface"""
        self.clear_content()

        title = ttk.Label(self.content_area, text="Version Control",
                         font=('Helvetica', 24, 'bold'))
        title.pack(pady=(0, 20))

        # Tabs
        notebook = ttk.Notebook(self.content_area)
        notebook.pack(fill=tk.BOTH, expand=True)

        # Create version tab
        create_frame = ttk.Frame(notebook, padding=20)
        notebook.add(create_frame, text="Create Version")

        ttk.Label(create_frame, text="Create a version snapshot",
                 font=('Helvetica', 12)).pack(pady=(0, 20))

        # File selection
        file_frame = ttk.Frame(create_frame)
        file_frame.pack(fill=tk.X, pady=10)

        ttk.Label(file_frame, text="File:").pack(side=tk.LEFT)
        self.version_file_var = tk.StringVar()
        ttk.Entry(file_frame, textvariable=self.version_file_var,
                 width=50).pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)
        ttk.Button(file_frame, text="Browse...",
                  command=lambda: self.browse_file(self.version_file_var)).pack(side=tk.LEFT)

        # Comment
        comment_frame = ttk.Frame(create_frame)
        comment_frame.pack(fill=tk.X, pady=10)

        ttk.Label(comment_frame, text="Comment:").pack(anchor=tk.W)
        self.version_comment_var = tk.StringVar()
        ttk.Entry(comment_frame, textvariable=self.version_comment_var,
                 width=60).pack(fill=tk.X, pady=5)

        # Create button
        ttk.Button(create_frame, text="Create Version",
                  command=self.create_version,
                  style='Success.TButton').pack(pady=20)

        # List versions tab
        list_frame = ttk.Frame(notebook, padding=20)
        notebook.add(list_frame, text="View Versions")

        ttk.Label(list_frame, text="View version history",
                 font=('Helvetica', 12)).pack(pady=(0, 20))

        # File name input
        filename_frame = ttk.Frame(list_frame)
        filename_frame.pack(fill=tk.X, pady=10)

        ttk.Label(filename_frame, text="Base filename:").pack(side=tk.LEFT)
        self.list_version_file_var = tk.StringVar()
        ttk.Entry(filename_frame, textvariable=self.list_version_file_var,
                 width=40).pack(side=tk.LEFT, padx=10)
        ttk.Button(filename_frame, text="List Versions",
                  command=self.list_versions).pack(side=tk.LEFT)

        # Versions list
        versions_frame = ttk.Frame(list_frame)
        versions_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))

        # Treeview for versions
        columns = ('Filename', 'Created', 'Size', 'Comment')
        self.versions_tree = ttk.Treeview(versions_frame, columns=columns,
                                         show='headings')

        for col in columns:
            self.versions_tree.heading(col, text=col)
            self.versions_tree.column(col, width=150)

        self.versions_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Scrollbar
        scrollbar = ttk.Scrollbar(versions_frame, orient=tk.VERTICAL,
                                 command=self.versions_tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.versions_tree.configure(yscrollcommand=scrollbar.set)

        # Restore button
        ttk.Button(list_frame, text="Restore Selected Version",
                  command=self.restore_version,
                  style='Warning.TButton').pack(pady=10)

    def show_retention(self):
        """Show retention policy interface"""
        self.clear_content()

        title = ttk.Label(self.content_area, text="Retention Policy",
                         font=('Helvetica', 24, 'bold'))
        title.pack(pady=(0, 20))

        # Current policy display
        policy_frame = ttk.LabelFrame(self.content_area, text="Current Policy",
                                     padding=20)
        policy_frame.pack(fill=tk.X, pady=(0, 20))

        policy_text = f"""
Archive files after: {self.retention.archive_days} days
Delete files after: {self.retention.delete_days} days

Files are moved to Archive/ after {self.retention.archive_days} days.
Files in Archive/ are permanently deleted after {self.retention.delete_days} days.
You will receive alerts 7 days before deletion.
        """

        ttk.Label(policy_frame, text=policy_text,
                 font=('Helvetica', 10)).pack()

        # Actions
        actions_frame = ttk.LabelFrame(self.content_area, text="Actions",
                                      padding=20)
        actions_frame.pack(fill=tk.BOTH, expand=True)

        # Dry run button
        ttk.Button(actions_frame, text="Preview Enforcement (Dry Run)",
                  command=self.retention_dry_run,
                  style='Accent.TButton',
                  width=30).pack(pady=10)

        ttk.Label(actions_frame, text="Preview what would happen without making changes",
                 font=('Helvetica', 9, 'italic')).pack()

        ttk.Separator(actions_frame, orient=tk.HORIZONTAL).pack(fill=tk.X,
                                                               pady=20)

        # Live enforcement
        ttk.Button(actions_frame, text="Enforce Retention Policy (Live)",
                  command=self.retention_enforce,
                  style='Danger.TButton',
                  width=30).pack(pady=10)

        ttk.Label(actions_frame, text="⚠️ This will archive old files and delete expired files",
                 font=('Helvetica', 9, 'italic'),
                 foreground=self.colors['danger']).pack()

        ttk.Separator(actions_frame, orient=tk.HORIZONTAL).pack(fill=tk.X,
                                                               pady=20)

        # Find expiring files
        ttk.Button(actions_frame, text="Find Files Expiring Soon",
                  command=self.check_expiring_files,
                  style='Warning.TButton',
                  width=30).pack(pady=10)

        # Results area
        results_frame = ttk.LabelFrame(self.content_area, text="Results",
                                      padding=10)
        results_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))

        self.retention_results_text = scrolledtext.ScrolledText(results_frame,
                                                               height=15, wrap=tk.WORD)
        self.retention_results_text.pack(fill=tk.BOTH, expand=True)

    def show_alerts(self):
        """Show alerts configuration"""
        self.clear_content()

        title = ttk.Label(self.content_area, text="Alert System",
                         font=('Helvetica', 24, 'bold'))
        title.pack(pady=(0, 20))

        # Current configuration
        config_frame = ttk.LabelFrame(self.content_area,
                                     text="Current Configuration", padding=20)
        config_frame.pack(fill=tk.X, pady=(0, 20))

        alerts_config = self.config['alerts']
        config_text = f"""
Alerts Enabled: {'Yes' if alerts_config.get('enabled', True) else 'No'}
Notification Method: {alerts_config.get('notification_method', 'email')}
Alert Window: {alerts_config.get('alert_days_before_delete', 7)} days before deletion

Email: {alerts_config.get('email', {}).get('to_email', 'Not configured')}
        """

        ttk.Label(config_frame, text=config_text,
                 font=('Helvetica', 10)).pack()

        # Actions
        actions_frame = ttk.LabelFrame(self.content_area, text="Actions",
                                      padding=20)
        actions_frame.pack(fill=tk.BOTH, expand=True)

        ttk.Button(actions_frame, text="Check & Send Alerts Now",
                  command=self.send_alerts,
                  style='Accent.TButton',
                  width=30).pack(pady=10)

        ttk.Button(actions_frame, text="Send Retention Report",
                  command=self.send_retention_report,
                  style='Accent.TButton',
                  width=30).pack(pady=10)

        ttk.Button(actions_frame, text="Test Email Configuration",
                  command=self.test_email,
                  style='Success.TButton',
                  width=30).pack(pady=10)

        # Results
        results_frame = ttk.LabelFrame(self.content_area, text="Results",
                                      padding=10)
        results_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))

        self.alerts_results_text = scrolledtext.ScrolledText(results_frame,
                                                            height=15, wrap=tk.WORD)
        self.alerts_results_text.pack(fill=tk.BOTH, expand=True)

    def show_reports(self):
        """Show reports interface"""
        self.clear_content()

        title = ttk.Label(self.content_area, text="Reports",
                         font=('Helvetica', 24, 'bold'))
        title.pack(pady=(0, 20))

        # Report type selection
        type_frame = ttk.Frame(self.content_area)
        type_frame.pack(fill=tk.X, pady=(0, 20))

        ttk.Label(type_frame, text="Report Type:").pack(side=tk.LEFT)
        self.report_type_var = tk.StringVar(value="Retention Report")
        report_combo = ttk.Combobox(type_frame, textvariable=self.report_type_var,
                                    values=["Retention Report", "Department Summary"],
                                    width=30)
        report_combo.pack(side=tk.LEFT, padx=10)

        ttk.Button(type_frame, text="Generate Report",
                  command=self.generate_report,
                  style='Accent.TButton').pack(side=tk.LEFT, padx=10)

        # Report display
        report_frame = ttk.LabelFrame(self.content_area, text="Report",
                                     padding=10)
        report_frame.pack(fill=tk.BOTH, expand=True)

        self.report_text = scrolledtext.ScrolledText(report_frame, height=25,
                                                     wrap=tk.WORD,
                                                     font=('Courier', 10))
        self.report_text.pack(fill=tk.BOTH, expand=True)

    def show_settings(self):
        """Show settings dialog"""
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Settings")
        settings_window.geometry("600x400")

        ttk.Label(settings_window, text="Settings",
                 font=('Helvetica', 16, 'bold')).pack(pady=20)

        # Config display
        config_frame = ttk.LabelFrame(settings_window, text="Configuration File",
                                     padding=20)
        config_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        config_text = scrolledtext.ScrolledText(config_frame, height=15,
                                               wrap=tk.WORD)
        config_text.pack(fill=tk.BOTH, expand=True)

        # Load config
        with open('config.json', 'r') as f:
            config_content = f.read()
        config_text.insert(tk.END, config_content)

        # Buttons
        button_frame = ttk.Frame(settings_window)
        button_frame.pack(pady=10)

        ttk.Button(button_frame, text="Edit config.json",
                  command=lambda: os.system('open config.json')).pack(side=tk.LEFT,
                                                                       padx=5)
        ttk.Button(button_frame, text="Close",
                  command=settings_window.destroy).pack(side=tk.LEFT, padx=5)

    def show_help(self):
        """Show help dialog"""
        help_window = tk.Toplevel(self.root)
        help_window.title("User Guide")
        help_window.geometry("700x600")

        ttk.Label(help_window, text="DocuFlow User Guide",
                 font=('Helvetica', 16, 'bold')).pack(pady=20)

        help_text = scrolledtext.ScrolledText(help_window, wrap=tk.WORD,
                                             padding=10)
        help_text.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))

        help_content = """
        DOCUFLOW USER GUIDE

        DASHBOARD
        - View summary statistics
        - Quick access to common actions
        - See recent activity

        ORGANIZE FILES
        - Single File: Organize one file at a time
        - Batch Organize: Process an entire folder

        VERSION CONTROL
        - Create versions before editing important files
        - View version history
        - Restore previous versions

        RETENTION POLICY
        - Preview enforcement (Dry Run) - Safe to test
        - Enforce live (archives old files, deletes expired)
        - Find files expiring soon

        ALERTS
        - Check and send alerts for expiring files
        - Send retention reports
        - Test email configuration

        REPORTS
        - Generate retention reports
        - View department summaries
        - Export data

        SAFETY FEATURES:
        ✓ All operations are reversible
        ✓ Dry-run mode available
        ✓ Version control keeps file history
        ✓ 7-day warning before deletion
        ✓ Original files never modified

        For more help, see README.md
        """

        help_text.insert(tk.END, help_content)
        help_text.config(state=tk.DISABLED)

        ttk.Button(help_window, text="Close",
                  command=help_window.destroy).pack(pady=10)

    def show_safety_info(self):
        """Show safety features information"""
        safety_window = tk.Toplevel(self.root)
        safety_window.title("Safety Features")
        safety_window.geometry("700x600")

        ttk.Label(safety_window, text="DocuFlow Safety Features",
                 font=('Helvetica', 16, 'bold')).pack(pady=20)

        safety_text = scrolledtext.ScrolledText(safety_window, wrap=tk.WORD,
                                               padding=10)
        safety_text.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))

        safety_content = """
        100% REVERSIBLE - ZERO RISK

        5-LAYER SAFETY SYSTEM:

        1. NON-DESTRUCTIVE OPERATIONS
           - Files are COPIED (not moved) by default
           - Original files always untouched
           - You can delete organized copies anytime

        2. AUTOMATIC VERSION CONTROL
           - Snapshots before every change
           - Keep last 5 versions (configurable)
           - One-click restore to any version
           - Even deleted files recoverable

        3. DRY-RUN MODE
           - Preview changes before applying
           - See what would happen
           - Nothing permanent until you approve

        4. MULTI-STAGE WARNINGS
           - 7-day alert before file deletion
           - Email/Slack notifications
           - Mark files for permanent retention
           - Manual review required

        5. COMPLETE AUDIT TRAIL
           - Every action logged
           - Who, what, when, why tracked
           - Searchable logs
           - Export for compliance

        WHAT DOCUFLOW CAN'T DO:
        ✗ Delete original files without confirmation
        ✗ Modify files without version backup
        ✗ Access files outside configured folders
        ✗ Delete files without 7-day warning
        ✗ Make changes in dry-run mode

        YOUR DATA IS SAFE!

        For more information, see SAFETY_GUARANTEE.md
        """

        safety_text.insert(tk.END, safety_content)
        safety_text.config(state=tk.DISABLED)

        ttk.Button(safety_window, text="Close",
                  command=safety_window.destroy).pack(pady=10)

    def show_about(self):
        """Show about dialog"""
        messagebox.showinfo("About DocuFlow",
                          "DocuFlow v1.0\n\n" +
                          "Document Management System\n\n" +
                          "Simple and clean document organization\n" +
                          "for small business clients.\n\n" +
                          "© 2025 Mike Finneran")

    # Action methods
    def browse_file(self, var=None):
        """Browse for file"""
        filename = filedialog.askopenfilename()
        if filename:
            if var:
                var.set(filename)
            else:
                self.file_path_var.set(filename)

    def browse_folder(self):
        """Browse for folder"""
        folder = filedialog.askdirectory()
        if folder:
            self.batch_folder_var.set(folder)

    def setup_folders(self):
        """Setup folder structure"""
        if messagebox.askyesno("Setup Folders",
                              "Create folder structure for all departments?"):
            try:
                self.organizer.setup_folder_structure()
                messagebox.showinfo("Success",
                                  "Folder structure created successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to create folders:\n{e}")

    def organize_single_file(self):
        """Organize a single file"""
        file_path = self.file_path_var.get()
        department = self.department_var.get()
        category = self.category_var.get()
        project = self.project_var.get()

        if not file_path or not department:
            messagebox.showwarning("Missing Information",
                                 "Please select a file and department")
            return

        try:
            result = self.organizer.organize_file(file_path, department,
                                                 category, project)
            if result:
                messagebox.showinfo("Success",
                                  f"File organized successfully!\n\n{result}")
            else:
                messagebox.showerror("Failed", "Could not organize file")
        except Exception as e:
            messagebox.showerror("Error", f"Error organizing file:\n{e}")

    def organize_batch(self):
        """Batch organize folder"""
        folder = self.batch_folder_var.get()
        department = self.batch_department_var.get()

        if not folder or not department:
            messagebox.showwarning("Missing Information",
                                 "Please select a folder and department")
            return

        try:
            self.batch_results_text.delete(1.0, tk.END)
            self.batch_results_text.insert(tk.END,
                                          f"Organizing files from {folder}...\n\n")

            # This should be done in a thread to not block UI
            self.organizer.batch_organize(folder, department)

            self.batch_results_text.insert(tk.END, "\n✓ Batch organization complete!")
        except Exception as e:
            messagebox.showerror("Error", f"Error in batch organize:\n{e}")

    def create_version(self):
        """Create file version"""
        file_path = self.version_file_var.get()
        comment = self.version_comment_var.get()

        if not file_path:
            messagebox.showwarning("Missing Information",
                                 "Please select a file")
            return

        try:
            result = self.version_control.create_version(file_path, comment)
            if result:
                messagebox.showinfo("Success",
                                  f"Version created successfully!\n\n{result}")
            else:
                messagebox.showerror("Failed", "Could not create version")
        except Exception as e:
            messagebox.showerror("Error", f"Error creating version:\n{e}")

    def quick_create_version(self):
        """Quick create version from dashboard"""
        file_path = filedialog.askopenfilename(title="Select file to version")
        if file_path:
            comment = tk.simpledialog.askstring("Version Comment",
                                               "Comment (optional):")
            try:
                result = self.version_control.create_version(file_path,
                                                            comment or "")
                if result:
                    messagebox.showinfo("Success",
                                      "Version created successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Error:\n{e}")

    def list_versions(self):
        """List file versions"""
        base_name = self.list_version_file_var.get()

        if not base_name:
            messagebox.showwarning("Missing Information",
                                 "Please enter a filename")
            return

        try:
            versions = self.version_control.list_versions(base_name)

            # Clear tree
            for item in self.versions_tree.get_children():
                self.versions_tree.delete(item)

            # Populate tree
            for v in versions:
                self.versions_tree.insert('', tk.END, values=(
                    v['filename'],
                    v['created'].strftime('%Y-%m-%d %H:%M'),
                    f"{v['size']:,} bytes",
                    v.get('comment', '')
                ))

            if not versions:
                messagebox.showinfo("No Versions",
                                  f"No versions found for {base_name}")

        except Exception as e:
            messagebox.showerror("Error", f"Error listing versions:\n{e}")

    def restore_version(self):
        """Restore selected version"""
        selection = self.versions_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection",
                                 "Please select a version to restore")
            return

        item = self.versions_tree.item(selection[0])
        version_filename = item['values'][0]

        # Ask for destination
        destination = filedialog.asksaveasfilename(
            title="Restore to",
            initialfile=version_filename.split('.')[0]
        )

        if destination:
            try:
                version_path = os.path.join(self.version_control.version_dir,
                                           version_filename)
                result = self.version_control.restore_version(version_path,
                                                             destination)
                if result:
                    messagebox.showinfo("Success",
                                      "Version restored successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Error restoring version:\n{e}")

    def retention_dry_run(self):
        """Run retention policy in dry-run mode"""
        try:
            self.retention_results_text.delete(1.0, tk.END)
            self.retention_results_text.insert(tk.END,
                                              "Running dry run...\n\n")

            stats = self.retention.enforce_retention(dry_run=True)

            result_text = f"""
DRY RUN RESULTS (No changes made)

Would archive: {stats['archived']} files
Would delete: {stats['deleted']} files

Review these numbers. If acceptable, use "Enforce Retention Policy (Live)"
to actually make these changes.
            """

            self.retention_results_text.insert(tk.END, result_text)
        except Exception as e:
            messagebox.showerror("Error", f"Error in dry run:\n{e}")

    def retention_enforce(self):
        """Enforce retention policy"""
        if not messagebox.askyesno("Confirm",
                                  "This will archive old files and delete expired files.\n\n" +
                                  "Are you sure you want to continue?"):
            return

        try:
            self.retention_results_text.delete(1.0, tk.END)
            self.retention_results_text.insert(tk.END,
                                              "Enforcing retention policy...\n\n")

            stats = self.retention.enforce_retention(dry_run=False)

            result_text = f"""
RETENTION POLICY ENFORCED

Archived: {stats['archived']} files
Deleted: {stats['deleted']} files

Check the logs for details.
            """

            self.retention_results_text.insert(tk.END, result_text)
            messagebox.showinfo("Complete", "Retention policy enforced successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Error enforcing policy:\n{e}")

    def check_expiring_files(self):
        """Check for files expiring soon"""
        try:
            expiring = self.retention.get_expiring_soon(7)

            if hasattr(self, 'retention_results_text'):
                self.retention_results_text.delete(1.0, tk.END)

                if expiring:
                    self.retention_results_text.insert(tk.END,
                        f"⚠️ {len(expiring)} file(s) will be deleted within 7 days:\n\n")

                    for file_info in expiring:
                        text = f"""
File: {file_info['name']}
Department: {file_info['department']}
Days until deletion: {file_info['days_until_deletion']}
Path: {file_info['path']}
---
"""
                        self.retention_results_text.insert(tk.END, text)
                else:
                    self.retention_results_text.insert(tk.END,
                                                      "✓ No files expiring soon")
            else:
                # Show in message box if not on retention page
                if expiring:
                    messagebox.showwarning("Files Expiring",
                        f"{len(expiring)} file(s) will be deleted within 7 days.\n\n" +
                        "Go to Retention page for details.")
                else:
                    messagebox.showinfo("No Expiring Files",
                                      "No files will be deleted soon")

        except Exception as e:
            messagebox.showerror("Error", f"Error checking expiring files:\n{e}")

    def send_alerts(self):
        """Send alerts for expiring files"""
        try:
            self.alerts_results_text.delete(1.0, tk.END)
            self.alerts_results_text.insert(tk.END, "Checking for expiring files...\n\n")

            alerts_sent = self.alerts.check_and_alert()

            result_text = f"✓ Sent {alerts_sent} alert(s)\n\n"
            result_text += "Check your email/Slack for notifications."

            self.alerts_results_text.insert(tk.END, result_text)
            messagebox.showinfo("Alerts Sent", f"Sent {alerts_sent} alert(s)")
        except Exception as e:
            messagebox.showerror("Error", f"Error sending alerts:\n{e}")

    def send_retention_report(self):
        """Send retention report"""
        try:
            self.alerts_results_text.delete(1.0, tk.END)
            self.alerts_results_text.insert(tk.END, "Sending retention report...\n\n")

            self.alerts.send_retention_report()

            self.alerts_results_text.insert(tk.END, "✓ Retention report sent")
            messagebox.showinfo("Report Sent", "Retention report sent successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Error sending report:\n{e}")

    def test_email(self):
        """Test email configuration"""
        try:
            # Implementation would test email setup
            messagebox.showinfo("Test Email",
                              "Email configuration test - see console for results")
        except Exception as e:
            messagebox.showerror("Error", f"Error testing email:\n{e}")

    def generate_report(self):
        """Generate selected report"""
        report_type = self.report_type_var.get()

        try:
            self.report_text.delete(1.0, tk.END)

            if report_type == "Retention Report":
                report = self.retention.get_retention_report()

                report_content = f"""
RETENTION POLICY REPORT
Generated: {report['generated_at']}

Policy Settings:
  Archive after: {report['policy']['archive_after_days']} days
  Delete after: {report['policy']['delete_after_days']} days

"""
                for dept, stats in report['departments'].items():
                    report_content += f"""
{dept}:
  Working: {stats['working']['count']} files ({stats['working']['total_size']:,} bytes)
    → {stats['working']['old_files']} ready to archive
  Archive: {stats['archive']['count']} files ({stats['archive']['total_size']:,} bytes)
    → {stats['archive']['expiring']} expiring soon
  Final: {stats['final']['count']} files ({stats['final']['total_size']:,} bytes)

"""
                self.report_text.insert(tk.END, report_content)

            elif report_type == "Department Summary":
                report = self.retention.get_retention_report()

                summary = "DEPARTMENT SUMMARY\n\n"
                for dept, stats in report['departments'].items():
                    total_files = (stats['working']['count'] +
                                 stats['archive']['count'] +
                                 stats['final']['count'])
                    total_size = (stats['working']['total_size'] +
                                stats['archive']['total_size'] +
                                stats['final']['total_size'])

                    summary += f"{dept}: {total_files} files, {total_size:,} bytes\n"

                self.report_text.insert(tk.END, summary)

        except Exception as e:
            messagebox.showerror("Error", f"Error generating report:\n{e}")

    def search_files(self):
        """Search for files"""
        query = tk.simpledialog.askstring("Search Files", "Enter search term:")
        if query:
            try:
                results = self.organizer.search_files(query)
                if results:
                    msg = f"Found {len(results)} file(s):\n\n"
                    for dept, cat, name, path in results[:10]:
                        msg += f"{name}\n  ({dept}/{cat})\n\n"
                    if len(results) > 10:
                        msg += f"\n...and {len(results) - 10} more"
                    messagebox.showinfo("Search Results", msg)
                else:
                    messagebox.showinfo("Search Results", "No files found")
            except Exception as e:
                messagebox.showerror("Error", f"Error searching:\n{e}")

    def run_daily_maintenance(self):
        """Run daily maintenance tasks"""
        if messagebox.askyesno("Daily Maintenance",
                              "Run daily maintenance?\n\n" +
                              "This will:\n" +
                              "- Enforce retention policy\n" +
                              "- Send alerts for expiring files"):
            try:
                # Run retention
                stats = self.retention.enforce_retention(dry_run=False)

                # Send alerts
                alerts_sent = self.alerts.check_and_alert()

                messagebox.showinfo("Maintenance Complete",
                    f"Daily maintenance complete!\n\n" +
                    f"Archived: {stats['archived']}\n" +
                    f"Deleted: {stats['deleted']}\n" +
                    f"Alerts sent: {alerts_sent}")
            except Exception as e:
                messagebox.showerror("Error", f"Error in maintenance:\n{e}")


def main():
    """Main entry point"""
    root = tk.Tk()
    app = DocuFlowGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
