#!/usr/bin/env python3
"""
DocuFlow - Retention Policy Module
Automated document archiving and deletion based on age
"""

import os
import shutil
import json
from datetime import datetime, timedelta
from pathlib import Path


class RetentionPolicy:
    """Document retention and disposal management"""

    def __init__(self, config_path="config.json"):
        """Initialize retention policy system"""
        with open(config_path, 'r') as f:
            self.config = json.load(f)

        self.policy = self.config['retention_policy']
        self.base_path = self.config['base_path']
        self.archive_days = self.policy['archive_after_days']
        self.delete_days = self.policy['delete_after_days']
        self.log_file = "retention_log.txt"

    def enforce_retention(self, department=None, dry_run=False):
        """
        Enforce retention policy across all or specific department

        Args:
            department: Specific department or None for all
            dry_run: If True, only report what would be done

        Returns:
            Dictionary with enforcement statistics
        """
        departments = [department] if department else self.config['folder_structure']['departments']

        stats = {
            'archived': 0,
            'deleted': 0,
            'scanned': 0,
            'errors': 0
        }

        now = datetime.now()

        for dept in departments:
            # Archive old files from Working
            working_folder = os.path.join(self.base_path, dept, "Working")
            if os.path.exists(working_folder):
                archived = self._archive_old_files(working_folder, dept, now, dry_run)
                stats['archived'] += archived

            # Delete expired files from Archive
            archive_folder = os.path.join(self.base_path, dept, "Archive")
            if os.path.exists(archive_folder):
                deleted = self._delete_expired_files(archive_folder, now, dry_run)
                stats['deleted'] += deleted

        self._log_enforcement(stats, dry_run)

        return stats

    def _archive_old_files(self, working_folder, department, now, dry_run):
        """Move files older than archive_days to Archive"""
        archive_folder = os.path.join(self.base_path, department, "Archive")
        os.makedirs(archive_folder, exist_ok=True)

        archived_count = 0
        archive_threshold = now - timedelta(days=self.archive_days)

        for file_name in os.listdir(working_folder):
            file_path = os.path.join(working_folder, file_name)

            if not os.path.isfile(file_path):
                continue

            # Check if excluded
            if self._is_excluded(file_name):
                continue

            # Get file modification time
            file_mtime = datetime.fromtimestamp(os.path.getmtime(file_path))

            if file_mtime < archive_threshold:
                dest_path = os.path.join(archive_folder, file_name)

                if dry_run:
                    print(f"  [DRY RUN] Would archive: {file_path}")
                else:
                    # Handle duplicate names in archive
                    if os.path.exists(dest_path):
                        base, ext = os.path.splitext(file_name)
                        dest_path = os.path.join(archive_folder, f"{base}_archived_{now.strftime('%Y%m%d')}{ext}")

                    shutil.move(file_path, dest_path)
                    self._log(f"Archived: {file_path} → {dest_path}")
                    print(f"  📦 Archived: {file_name}")

                archived_count += 1

        return archived_count

    def _delete_expired_files(self, archive_folder, now, dry_run):
        """Delete files older than delete_days from Archive"""
        deleted_count = 0
        delete_threshold = now - timedelta(days=self.delete_days)

        for file_name in os.listdir(archive_folder):
            file_path = os.path.join(archive_folder, file_name)

            if not os.path.isfile(file_path):
                continue

            # Check if excluded
            if self._is_excluded(file_name):
                continue

            # Get file modification time
            file_mtime = datetime.fromtimestamp(os.path.getmtime(file_path))

            if file_mtime < delete_threshold:
                if dry_run:
                    print(f"  [DRY RUN] Would delete: {file_path}")
                else:
                    os.remove(file_path)
                    self._log(f"Deleted (retention expired): {file_path}")
                    print(f"  🗑️  Deleted: {file_name}")

                deleted_count += 1

        return deleted_count

    def get_expiring_soon(self, days_until_deletion=7, department=None):
        """
        Find files that will be deleted within X days

        Args:
            days_until_deletion: Warning threshold in days
            department: Specific department or None for all

        Returns:
            List of files nearing deletion
        """
        departments = [department] if department else self.config['folder_structure']['departments']

        expiring_files = []
        now = datetime.now()
        warning_threshold = now - timedelta(days=self.delete_days - days_until_deletion)
        delete_threshold = now - timedelta(days=self.delete_days)

        for dept in departments:
            archive_folder = os.path.join(self.base_path, dept, "Archive")

            if not os.path.exists(archive_folder):
                continue

            for file_name in os.listdir(archive_folder):
                file_path = os.path.join(archive_folder, file_name)

                if not os.path.isfile(file_path):
                    continue

                file_mtime = datetime.fromtimestamp(os.path.getmtime(file_path))

                # Check if file is in warning window
                if warning_threshold <= file_mtime < delete_threshold:
                    days_until = (file_mtime - delete_threshold).days
                    expiring_files.append({
                        'path': file_path,
                        'name': file_name,
                        'department': dept,
                        'modified': file_mtime,
                        'days_until_deletion': abs(days_until)
                    })

        return sorted(expiring_files, key=lambda x: x['days_until_deletion'])

    def mark_for_retention(self, file_path):
        """
        Mark a file to be kept (exempt from deletion)

        Args:
            file_path: Path to file to keep

        Note: This creates a .keep marker file
        """
        if not os.path.exists(file_path):
            print(f"❌ File not found: {file_path}")
            return False

        keep_marker = f"{file_path}.keep"

        with open(keep_marker, 'w') as f:
            f.write(json.dumps({
                'marked_by': os.getenv('USER', 'unknown'),
                'marked_at': datetime.now().isoformat(),
                'reason': 'Manual retention'
            }, indent=2))

        self._log(f"Marked for retention: {file_path}")
        print(f"✅ Marked for retention: {os.path.basename(file_path)}")

        return True

    def get_retention_report(self, department=None):
        """
        Generate retention policy compliance report

        Args:
            department: Specific department or None for all

        Returns:
            Dictionary with report data
        """
        departments = [department] if department else self.config['folder_structure']['departments']

        report = {
            'generated_at': datetime.now().isoformat(),
            'policy': {
                'archive_after_days': self.archive_days,
                'delete_after_days': self.delete_days
            },
            'departments': {}
        }

        now = datetime.now()

        for dept in departments:
            dept_stats = {
                'working': {'count': 0, 'total_size': 0, 'old_files': 0},
                'archive': {'count': 0, 'total_size': 0, 'expiring': 0},
                'final': {'count': 0, 'total_size': 0}
            }

            # Scan each category
            for category in ['Working', 'Archive', 'Final']:
                folder = os.path.join(self.base_path, dept, category)
                if not os.path.exists(folder):
                    continue

                cat_key = category.lower()

                for file_name in os.listdir(folder):
                    file_path = os.path.join(folder, file_name)

                    if not os.path.isfile(file_path):
                        continue

                    file_size = os.path.getsize(file_path)
                    file_age = (now - datetime.fromtimestamp(os.path.getmtime(file_path))).days

                    dept_stats[cat_key]['count'] += 1
                    dept_stats[cat_key]['total_size'] += file_size

                    # Check if file should be archived
                    if category == 'Working' and file_age > self.archive_days:
                        dept_stats[cat_key]['old_files'] += 1

                    # Check if file will expire soon
                    if category == 'Archive' and file_age > (self.delete_days - 7):
                        dept_stats[cat_key]['expiring'] += 1

            report['departments'][dept] = dept_stats

        return report

    def _is_excluded(self, filename):
        """Check if file should be excluded from retention"""
        exclusions = self.config.get('exclusions', {}).get('files', [])

        for pattern in exclusions:
            if filename == pattern or filename.endswith(pattern):
                return True

        # Check for .keep marker
        return False

    def _log(self, message):
        """Write to retention log"""
        with open(self.log_file, 'a') as log:
            timestamp = datetime.now().isoformat()
            log.write(f"{timestamp} | {message}\n")

    def _log_enforcement(self, stats, dry_run):
        """Log retention enforcement run"""
        mode = "DRY RUN" if dry_run else "ENFORCED"
        message = f"Retention {mode}: Archived={stats['archived']}, Deleted={stats['deleted']}"
        self._log(message)


def main():
    """Example usage and CLI"""
    print("=" * 80)
    print("DocuFlow - Retention Policy Management")
    print("=" * 80)

    rp = RetentionPolicy()

    print(f"\nCurrent Policy:")
    print(f"  Archive after: {rp.archive_days} days")
    print(f"  Delete after: {rp.delete_days} days")

    print("\nAvailable commands:")
    print("1. Enforce retention (dry run)")
    print("2. Enforce retention (live)")
    print("3. Find files expiring soon")
    print("4. Mark file for retention")
    print("5. Generate retention report")

    choice = input("\nEnter choice (1-5): ").strip()

    if choice == "1":
        print("\n🔍 Running dry run...")
        stats = rp.enforce_retention(dry_run=True)
        print(f"\n📊 Would archive {stats['archived']} and delete {stats['deleted']} files")

    elif choice == "2":
        confirm = input("\n⚠️  This will archive and delete files. Continue? (yes/no): ").strip().lower()
        if confirm == 'yes':
            stats = rp.enforce_retention(dry_run=False)
            print(f"\n✅ Archived {stats['archived']} and deleted {stats['deleted']} files")
        else:
            print("Cancelled")

    elif choice == "3":
        days = input("Alert for files expiring within how many days? (default 7): ").strip()
        days = int(days) if days else 7

        expiring = rp.get_expiring_soon(days)

        print(f"\n⚠️  {len(expiring)} file(s) will be deleted within {days} days:")
        for file_info in expiring:
            print(f"\n  {file_info['name']}")
            print(f"    Department: {file_info['department']}")
            print(f"    Days until deletion: {file_info['days_until_deletion']}")

    elif choice == "4":
        file_path = input("File path: ").strip()
        rp.mark_for_retention(file_path)

    elif choice == "5":
        report = rp.get_retention_report()

        print(f"\n📋 Retention Report - Generated: {report['generated_at']}")
        print(f"\nPolicy: Archive after {report['policy']['archive_after_days']} days, Delete after {report['policy']['delete_after_days']} days\n")

        for dept, stats in report['departments'].items():
            print(f"\n{dept}:")
            print(f"  Working: {stats['working']['count']} files ({stats['working']['total_size']:,} bytes)")
            print(f"    - {stats['working']['old_files']} ready to archive")
            print(f"  Archive: {stats['archive']['count']} files ({stats['archive']['total_size']:,} bytes)")
            print(f"    - {stats['archive']['expiring']} expiring soon")
            print(f"  Final: {stats['final']['count']} files ({stats['final']['total_size']:,} bytes)")


if __name__ == "__main__":
    main()
