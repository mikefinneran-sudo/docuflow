#!/usr/bin/env python3
"""
DocuFlow - Complete Document Management System
Main control interface for all modules
"""

import os
import sys
from document_organizer import DocumentOrganizer
from version_control import VersionControl
from retention_policy import RetentionPolicy
from alert_system import AlertSystem


class DocuFlow:
    """Main DocuFlow system controller"""

    def __init__(self, config_path="config.json"):
        """Initialize all DocuFlow modules"""
        self.organizer = DocumentOrganizer(config_path)
        self.version_control = VersionControl(config_path)
        self.retention = RetentionPolicy(config_path)
        self.alerts = AlertSystem(config_path)

    def main_menu(self):
        """Display main menu and handle user input"""
        while True:
            self._display_menu()
            choice = input("\nEnter choice (or 'q' to quit): ").strip().lower()

            if choice == 'q':
                print("\n👋 Goodbye!")
                break

            self._handle_choice(choice)

    def _display_menu(self):
        """Display main menu"""
        print("\n" + "=" * 80)
        print("DocuFlow - Document Management System")
        print("=" * 80)

        print("\n📁 ORGANIZATION")
        print("  1. Setup folder structure")
        print("  2. Organize single file")
        print("  3. Batch organize folder")
        print("  4. List files")
        print("  5. Search files")

        print("\n📝 VERSION CONTROL")
        print("  6. Create version")
        print("  7. List versions")
        print("  8. Restore version")
        print("  9. Version history")

        print("\n📦 RETENTION POLICY")
        print("  10. Run retention enforcement (dry run)")
        print("  11. Run retention enforcement (live)")
        print("  12. Find expiring files")
        print("  13. Retention report")

        print("\n🔔 ALERTS")
        print("  14. Check and send alerts")
        print("  15. Send retention report")

        print("\n⚙️  SYSTEM")
        print("  16. Quick setup (new client)")
        print("  17. Daily maintenance")
        print("  q. Quit")

    def _handle_choice(self, choice):
        """Handle user menu choice"""
        try:
            if choice == '1':
                self._setup_structure()
            elif choice == '2':
                self._organize_file()
            elif choice == '3':
                self._batch_organize()
            elif choice == '4':
                self._list_files()
            elif choice == '5':
                self._search_files()
            elif choice == '6':
                self._create_version()
            elif choice == '7':
                self._list_versions()
            elif choice == '8':
                self._restore_version()
            elif choice == '9':
                self._version_history()
            elif choice == '10':
                self._retention_dry_run()
            elif choice == '11':
                self._retention_live()
            elif choice == '12':
                self._find_expiring()
            elif choice == '13':
                self._retention_report()
            elif choice == '14':
                self._check_alerts()
            elif choice == '15':
                self._send_report()
            elif choice == '16':
                self._quick_setup()
            elif choice == '17':
                self._daily_maintenance()
            else:
                print("❌ Invalid choice")

        except KeyboardInterrupt:
            print("\n\n⏸️  Operation cancelled")
        except Exception as e:
            print(f"\n❌ Error: {e}")

    # Organization functions
    def _setup_structure(self):
        """Setup folder structure"""
        print("\n--- Setup Folder Structure ---")
        dept = input("Department (or blank for all): ").strip() or None
        self.organizer.setup_folder_structure(dept)

    def _organize_file(self):
        """Organize single file"""
        print("\n--- Organize File ---")
        file_path = input("File path: ").strip()
        department = input("Department: ").strip()
        category = input("Category (Working/Final/Archive) [Working]: ").strip() or "Working"
        project = input("Project name (optional): ").strip()

        self.organizer.organize_file(file_path, department, category, project)

    def _batch_organize(self):
        """Batch organize folder"""
        print("\n--- Batch Organize ---")
        source = input("Source folder: ").strip()
        department = input("Department: ").strip()

        self.organizer.batch_organize(source, department)

    def _list_files(self):
        """List files"""
        print("\n--- List Files ---")
        department = input("Department: ").strip()
        category = input("Category (or blank for all): ").strip() or None

        self.organizer.list_files(department, category)

    def _search_files(self):
        """Search files"""
        print("\n--- Search Files ---")
        query = input("Search term: ").strip()

        self.organizer.search_files(query)

    # Version control functions
    def _create_version(self):
        """Create file version"""
        print("\n--- Create Version ---")
        file_path = input("File path: ").strip()
        comment = input("Comment (optional): ").strip()

        self.version_control.create_version(file_path, comment)

    def _list_versions(self):
        """List file versions"""
        print("\n--- List Versions ---")
        base_name = input("Base filename: ").strip()

        versions = self.version_control.list_versions(base_name)

        print(f"\n📋 Found {len(versions)} version(s):")
        for v in versions:
            print(f"\n  {v['filename']}")
            print(f"    Created: {v['created'].strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"    Size: {v['size']:,} bytes")
            if 'comment' in v:
                print(f"    Comment: {v['comment']}")

    def _restore_version(self):
        """Restore file version"""
        print("\n--- Restore Version ---")
        version_path = input("Version path: ").strip()
        destination = input("Restore to: ").strip()

        self.version_control.restore_version(version_path, destination)

    def _version_history(self):
        """Show version history"""
        print("\n--- Version History ---")
        base_name = input("Base filename: ").strip()
        limit = input("Max versions (or blank for all): ").strip()
        limit = int(limit) if limit else None

        history = self.version_control.get_version_history(base_name, limit)

        print(f"\n📜 Version History ({len(history)} versions):")
        for i, v in enumerate(history, 1):
            print(f"\n{i}. {v['filename']}")
            print(f"   Created: {v['created'].strftime('%Y-%m-%d %H:%M:%S')}")
            if 'comment' in v:
                print(f"   Comment: {v['comment']}")

    # Retention functions
    def _retention_dry_run(self):
        """Run retention dry run"""
        print("\n--- Retention Policy (Dry Run) ---")
        stats = self.retention.enforce_retention(dry_run=True)

        print(f"\n📊 Dry Run Results:")
        print(f"  Would archive: {stats['archived']} files")
        print(f"  Would delete: {stats['deleted']} files")

    def _retention_live(self):
        """Run retention live"""
        print("\n--- Retention Policy (Live Enforcement) ---")
        print("⚠️  This will archive old files and delete expired files")

        confirm = input("Continue? (yes/no): ").strip().lower()
        if confirm != 'yes':
            print("Cancelled")
            return

        stats = self.retention.enforce_retention(dry_run=False)

        print(f"\n✅ Enforcement Complete:")
        print(f"  Archived: {stats['archived']} files")
        print(f"  Deleted: {stats['deleted']} files")

    def _find_expiring(self):
        """Find expiring files"""
        print("\n--- Find Expiring Files ---")
        days = input("Alert for files expiring within how many days? [7]: ").strip()
        days = int(days) if days else 7

        expiring = self.retention.get_expiring_soon(days)

        print(f"\n⚠️  {len(expiring)} file(s) will be deleted within {days} days:")
        for file_info in expiring:
            print(f"\n  {file_info['name']}")
            print(f"    Department: {file_info['department']}")
            print(f"    Days until deletion: {file_info['days_until_deletion']}")
            print(f"    Path: {file_info['path']}")

    def _retention_report(self):
        """Generate retention report"""
        print("\n--- Retention Report ---")
        report = self.retention.get_retention_report()

        print(f"\n📋 Report Generated: {report['generated_at']}")
        print(f"\nPolicy: Archive after {report['policy']['archive_after_days']} days, Delete after {report['policy']['delete_after_days']} days")

        for dept, stats in report['departments'].items():
            print(f"\n{dept}:")
            print(f"  Working: {stats['working']['count']} files ({stats['working']['total_size']:,} bytes)")
            print(f"    → {stats['working']['old_files']} ready to archive")
            print(f"  Archive: {stats['archive']['count']} files ({stats['archive']['total_size']:,} bytes)")
            print(f"    → {stats['archive']['expiring']} expiring soon")
            print(f"  Final: {stats['final']['count']} files ({stats['final']['total_size']:,} bytes)")

    # Alert functions
    def _check_alerts(self):
        """Check and send alerts"""
        print("\n--- Check Alerts ---")
        alerts_sent = self.alerts.check_and_alert()
        print(f"\n✅ Sent {alerts_sent} alert(s)")

    def _send_report(self):
        """Send retention report"""
        print("\n--- Send Retention Report ---")
        self.alerts.send_retention_report()

    # System functions
    def _quick_setup(self):
        """Quick setup for new client"""
        print("\n" + "=" * 80)
        print("DocuFlow - Quick Setup")
        print("=" * 80)

        print("\n1️⃣  Creating folder structure...")
        self.organizer.setup_folder_structure()

        print("\n2️⃣  Setting up version control...")
        print(f"   Version directory: {self.version_control.version_dir}")
        print(f"   Max versions: {self.version_control.max_versions}")

        print("\n3️⃣  Configuring retention policy...")
        print(f"   Archive after: {self.retention.archive_days} days")
        print(f"   Delete after: {self.retention.delete_days} days")

        print("\n4️⃣  Setting up alerts...")
        print(f"   Alert method: {self.alerts.notification_method}")
        print(f"   Alert window: {self.alerts.alert_days} days before deletion")

        print("\n✅ Quick setup complete!")
        print("\nNext steps:")
        print("  1. Configure email settings in config.json")
        print("  2. Start organizing documents (option 2 or 3)")
        print("  3. Schedule daily maintenance (cron/Task Scheduler)")

    def _daily_maintenance(self):
        """Run daily maintenance tasks"""
        print("\n" + "=" * 80)
        print("DocuFlow - Daily Maintenance")
        print("=" * 80)

        # 1. Enforce retention policy
        print("\n1️⃣  Enforcing retention policy...")
        stats = self.retention.enforce_retention(dry_run=False)
        print(f"   Archived: {stats['archived']}, Deleted: {stats['deleted']}")

        # 2. Check for expiring files
        print("\n2️⃣  Checking for expiring files...")
        alerts_sent = self.alerts.check_and_alert()
        print(f"   Alerts sent: {alerts_sent}")

        # 3. Clean up old versions
        print("\n3️⃣  Version cleanup already handled by retention")

        print("\n✅ Daily maintenance complete!")


def main():
    """Main entry point"""
    try:
        docuflow = DocuFlow()
        docuflow.main_menu()
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
