#!/usr/bin/env python3
"""
DocuFlow - Document Organization System
Main organizer module for automated file management
"""

import os
import shutil
import json
from datetime import datetime
from pathlib import Path


class DocumentOrganizer:
    """Core document organization and filing system"""

    def __init__(self, config_path="config.json"):
        """Initialize with configuration file"""
        with open(config_path, 'r') as f:
            self.config = json.load(f)

        self.base_path = self.config['base_path']
        self.client_name = self.config['client_name']
        self.log_file = "organization_log.txt"

    def setup_folder_structure(self, department=None):
        """
        Create standardized folder structure

        Args:
            department: Specific department to create, or None for all
        """
        departments = [department] if department else self.config['folder_structure']['departments']
        categories = self.config['folder_structure']['categories']

        for dept in departments:
            for category in categories:
                folder_path = os.path.join(self.base_path, dept, category)
                os.makedirs(folder_path, exist_ok=True)
                self._log(f"Created folder: {folder_path}")

        print(f"✅ Folder structure created for {len(departments)} department(s)")

    def generate_filename(self, original_name, project_name="", version=1):
        """
        Generate standardized filename based on naming convention

        Args:
            original_name: Original filename
            project_name: Project or document type
            version: Version number

        Returns:
            Standardized filename
        """
        # Extract extension
        name, ext = os.path.splitext(original_name)
        ext = ext.lstrip('.')

        # Get date
        date_str = datetime.now().strftime(self.config['naming_convention']['date_format'])

        # Build filename
        pattern = self.config['naming_convention']['pattern']
        new_name = pattern.format(
            client=self.client_name.replace(' ', '_'),
            project=project_name or name,
            date=date_str,
            version=version,
            ext=ext
        )

        return new_name

    def organize_file(self, file_path, department, category="Working", project_name=""):
        """
        Organize a file into the proper folder with standardized naming

        Args:
            file_path: Path to file to organize
            department: Target department folder
            category: Working, Final, or Archive
            project_name: Optional project name for filename
        """
        if not os.path.exists(file_path):
            print(f"❌ File not found: {file_path}")
            return False

        # Generate new filename
        original_name = os.path.basename(file_path)
        new_name = self.generate_filename(original_name, project_name)

        # Determine destination
        dest_folder = os.path.join(self.base_path, department, category)
        os.makedirs(dest_folder, exist_ok=True)

        dest_path = os.path.join(dest_folder, new_name)

        # Handle existing file
        if os.path.exists(dest_path):
            # Auto-increment version if enabled
            if self.config['naming_convention']['auto_version']:
                version = 2
                while os.path.exists(dest_path):
                    new_name = self.generate_filename(original_name, project_name, version)
                    dest_path = os.path.join(dest_folder, new_name)
                    version += 1
            else:
                print(f"⚠️  File already exists: {dest_path}")
                return False

        # Copy file
        shutil.copy2(file_path, dest_path)
        self._log(f"Organized: {file_path} → {dest_path}")
        print(f"✅ Organized: {new_name}")

        return dest_path

    def batch_organize(self, source_folder, department, file_types=None):
        """
        Organize all files from a source folder

        Args:
            source_folder: Folder containing files to organize
            department: Target department
            file_types: List of extensions to process (e.g., ['.pdf', '.docx'])
        """
        if not os.path.exists(source_folder):
            print(f"❌ Source folder not found: {source_folder}")
            return

        # Get all files
        files = [f for f in os.listdir(source_folder)
                if os.path.isfile(os.path.join(source_folder, f))]

        # Filter by type if specified
        if file_types:
            files = [f for f in files if any(f.lower().endswith(ext) for ext in file_types)]

        organized_count = 0
        for file_name in files:
            file_path = os.path.join(source_folder, file_name)
            if self.organize_file(file_path, department):
                organized_count += 1

        print(f"\n📊 Organized {organized_count}/{len(files)} files from {source_folder}")

    def move_to_final(self, file_path, department):
        """
        Move a document from Working to Final

        Args:
            file_path: Path to file in Working folder
            department: Department folder
        """
        if not os.path.exists(file_path):
            print(f"❌ File not found: {file_path}")
            return False

        # Determine paths
        file_name = os.path.basename(file_path)
        final_folder = os.path.join(self.base_path, department, "Final")
        os.makedirs(final_folder, exist_ok=True)

        dest_path = os.path.join(final_folder, file_name)

        # Move file
        shutil.move(file_path, dest_path)
        self._log(f"Finalized: {file_path} → {dest_path}")
        print(f"✅ Moved to Final: {file_name}")

        return dest_path

    def archive_old_files(self, department, days=None):
        """
        Move files older than X days from Working to Archive

        Args:
            department: Department to process
            days: Age threshold (uses config if not specified)
        """
        if days is None:
            days = self.config['retention_policy']['archive_after_days']

        working_folder = os.path.join(self.base_path, department, "Working")
        archive_folder = os.path.join(self.base_path, department, "Archive")

        if not os.path.exists(working_folder):
            print(f"⚠️  Working folder not found: {working_folder}")
            return

        os.makedirs(archive_folder, exist_ok=True)

        now = datetime.now().timestamp()
        archived_count = 0

        for file_name in os.listdir(working_folder):
            file_path = os.path.join(working_folder, file_name)

            if not os.path.isfile(file_path):
                continue

            # Check age
            file_age_days = (now - os.path.getmtime(file_path)) / 86400

            if file_age_days > days:
                dest_path = os.path.join(archive_folder, file_name)
                shutil.move(file_path, dest_path)
                self._log(f"Archived: {file_path} → {dest_path}")
                archived_count += 1

        print(f"📦 Archived {archived_count} file(s) older than {days} days from {department}")

    def list_files(self, department, category=None):
        """
        List all files in a department/category

        Args:
            department: Department folder
            category: Optional category (Working/Final/Archive)
        """
        if category:
            folders = [os.path.join(self.base_path, department, category)]
        else:
            categories = self.config['folder_structure']['categories']
            folders = [os.path.join(self.base_path, department, cat) for cat in categories]

        print(f"\n📁 Files in {department}" + (f"/{category}" if category else ""))
        print("=" * 80)

        for folder in folders:
            if not os.path.exists(folder):
                continue

            folder_name = os.path.basename(folder)
            files = [f for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f))]

            if files:
                print(f"\n{folder_name}/ ({len(files)} files)")
                for file_name in sorted(files):
                    file_path = os.path.join(folder, file_name)
                    file_size = os.path.getsize(file_path)
                    mod_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                    print(f"  - {file_name}")
                    print(f"    Size: {file_size:,} bytes | Modified: {mod_time.strftime('%Y-%m-%d %H:%M')}")

    def search_files(self, query, department=None):
        """
        Search for files by name across all departments

        Args:
            query: Search term
            department: Optional specific department
        """
        departments = [department] if department else self.config['folder_structure']['departments']
        categories = self.config['folder_structure']['categories']

        results = []

        for dept in departments:
            for cat in categories:
                folder = os.path.join(self.base_path, dept, cat)
                if not os.path.exists(folder):
                    continue

                for file_name in os.listdir(folder):
                    if query.lower() in file_name.lower():
                        file_path = os.path.join(folder, file_name)
                        results.append((dept, cat, file_name, file_path))

        print(f"\n🔍 Search results for '{query}': {len(results)} found")
        print("=" * 80)

        for dept, cat, file_name, file_path in results:
            print(f"\n{dept}/{cat}/{file_name}")
            print(f"  Path: {file_path}")
            mod_time = datetime.fromtimestamp(os.path.getmtime(file_path))
            print(f"  Modified: {mod_time.strftime('%Y-%m-%d %H:%M')}")

        return results

    def _log(self, message):
        """Write to log file"""
        with open(self.log_file, 'a') as log:
            timestamp = datetime.now().isoformat()
            log.write(f"{timestamp} | {message}\n")


def main():
    """Example usage and CLI interface"""
    print("=" * 80)
    print("DocuFlow - Document Organization System")
    print("=" * 80)

    organizer = DocumentOrganizer()

    print("\nAvailable commands:")
    print("1. Setup folder structure")
    print("2. Organize a file")
    print("3. Batch organize folder")
    print("4. List files")
    print("5. Search files")
    print("6. Archive old files")

    choice = input("\nEnter choice (1-6): ").strip()

    if choice == "1":
        organizer.setup_folder_structure()

    elif choice == "2":
        file_path = input("File path: ").strip()
        department = input("Department (Finance/HR/Operations/Sales/Legal): ").strip()
        project = input("Project name (optional): ").strip()
        organizer.organize_file(file_path, department, project_name=project)

    elif choice == "3":
        source = input("Source folder: ").strip()
        department = input("Department: ").strip()
        organizer.batch_organize(source, department)

    elif choice == "4":
        department = input("Department: ").strip()
        category = input("Category (Working/Final/Archive, or leave blank): ").strip() or None
        organizer.list_files(department, category)

    elif choice == "5":
        query = input("Search term: ").strip()
        organizer.search_files(query)

    elif choice == "6":
        department = input("Department: ").strip()
        days = input("Archive files older than (days): ").strip()
        organizer.archive_old_files(department, int(days) if days else None)


if __name__ == "__main__":
    main()
