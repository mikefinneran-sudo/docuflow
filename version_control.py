#!/usr/bin/env python3
"""
DocuFlow - Version Control Module
Automatic file versioning with metadata tracking
"""

import os
import shutil
import json
import hashlib
from datetime import datetime
from pathlib import Path


class VersionControl:
    """File version control system with metadata tracking"""

    def __init__(self, config_path="config.json"):
        """Initialize version control system"""
        with open(config_path, 'r') as f:
            self.config = json.load(f)

        self.vc_config = self.config['version_control']
        self.version_dir = self.vc_config['version_dir']
        self.max_versions = self.vc_config['max_versions']
        self.track_metadata = self.vc_config['track_metadata']

        os.makedirs(self.version_dir, exist_ok=True)

    def create_version(self, file_path, comment=""):
        """
        Create a new version of a file

        Args:
            file_path: Path to file to version
            comment: Optional comment describing the changes

        Returns:
            Path to versioned file
        """
        if not os.path.exists(file_path):
            print(f"❌ File not found: {file_path}")
            return None

        # Generate version info
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_name = os.path.basename(file_path)
        version_name = f"{base_name}.{timestamp}"
        version_path = os.path.join(self.version_dir, version_name)

        # Copy file to versions folder
        shutil.copyfile(file_path, version_path)

        # Create metadata
        if self.track_metadata:
            metadata = self._generate_metadata(file_path, version_path, comment)
            meta_path = f"{version_path}.json"

            with open(meta_path, 'w') as f:
                json.dump(metadata, f, indent=2)

        print(f"✅ Version created: {version_name}")

        # Clean up old versions
        self._cleanup_old_versions(base_name)

        return version_path

    def list_versions(self, base_filename):
        """
        List all versions of a file

        Args:
            base_filename: Original filename (without version suffix)

        Returns:
            List of version info dictionaries
        """
        versions = []

        # Find all versions of this file
        for file_name in sorted(os.listdir(self.version_dir), reverse=True):
            if file_name.startswith(base_filename) and not file_name.endswith('.json'):
                version_path = os.path.join(self.version_dir, file_name)
                meta_path = f"{version_path}.json"

                version_info = {
                    'filename': file_name,
                    'path': version_path,
                    'created': datetime.fromtimestamp(os.path.getctime(version_path)),
                    'size': os.path.getsize(version_path)
                }

                # Load metadata if available
                if os.path.exists(meta_path):
                    with open(meta_path, 'r') as f:
                        metadata = json.load(f)
                        version_info.update(metadata)

                versions.append(version_info)

        return versions

    def restore_version(self, version_path, destination):
        """
        Restore a specific version to a destination

        Args:
            version_path: Path to versioned file
            destination: Where to restore the file

        Returns:
            Path to restored file
        """
        if not os.path.exists(version_path):
            print(f"❌ Version not found: {version_path}")
            return None

        # Create backup of current file if it exists
        if os.path.exists(destination):
            backup_comment = f"Auto-backup before restoring {os.path.basename(version_path)}"
            self.create_version(destination, backup_comment)

        # Restore version
        shutil.copyfile(version_path, destination)
        print(f"✅ Restored version: {os.path.basename(version_path)} → {destination}")

        return destination

    def compare_versions(self, version1_path, version2_path):
        """
        Compare two versions

        Args:
            version1_path: Path to first version
            version2_path: Path to second version

        Returns:
            Dictionary with comparison results
        """
        if not os.path.exists(version1_path) or not os.path.exists(version2_path):
            print("❌ One or both versions not found")
            return None

        comparison = {
            'version1': os.path.basename(version1_path),
            'version2': os.path.basename(version2_path),
            'size_diff': os.path.getsize(version2_path) - os.path.getsize(version1_path),
            'identical': self._get_file_hash(version1_path) == self._get_file_hash(version2_path)
        }

        # Get metadata if available
        for i, path in enumerate([version1_path, version2_path], 1):
            meta_path = f"{path}.json"
            if os.path.exists(meta_path):
                with open(meta_path, 'r') as f:
                    comparison[f'metadata{i}'] = json.load(f)

        return comparison

    def get_version_history(self, base_filename, limit=None):
        """
        Get version history for a file

        Args:
            base_filename: Original filename
            limit: Max number of versions to return

        Returns:
            List of versions sorted by date (newest first)
        """
        versions = self.list_versions(base_filename)

        if limit:
            versions = versions[:limit]

        return versions

    def auto_version_on_change(self, file_path, check_interval=60):
        """
        Monitor a file and auto-create versions when changed

        Args:
            file_path: File to monitor
            check_interval: Seconds between checks

        Note: This is a blocking operation for demonstration.
        In production, use a file watcher library like watchdog.
        """
        import time

        if not os.path.exists(file_path):
            print(f"❌ File not found: {file_path}")
            return

        print(f"👁️  Monitoring {file_path} for changes...")
        print(f"   (Press Ctrl+C to stop)")

        last_hash = self._get_file_hash(file_path)
        last_version_time = datetime.now()

        try:
            while True:
                time.sleep(check_interval)

                if not os.path.exists(file_path):
                    print("⚠️  File no longer exists")
                    break

                current_hash = self._get_file_hash(file_path)

                if current_hash != last_hash:
                    # File changed
                    time_since_last = (datetime.now() - last_version_time).total_seconds()

                    # Only version if enough time has passed (avoid too frequent versions)
                    if time_since_last > check_interval:
                        comment = f"Auto-version (file changed)"
                        self.create_version(file_path, comment)
                        last_hash = current_hash
                        last_version_time = datetime.now()

        except KeyboardInterrupt:
            print("\n✋ Monitoring stopped")

    def _generate_metadata(self, original_path, version_path, comment):
        """Generate metadata for a version"""
        return {
            'original_file': os.path.basename(original_path),
            'original_path': original_path,
            'version_path': version_path,
            'version_timestamp': datetime.now().isoformat(),
            'file_size': os.path.getsize(version_path),
            'file_hash': self._get_file_hash(version_path),
            'comment': comment,
            'modified_by': os.getenv('USER', 'unknown')
        }

    def _get_file_hash(self, file_path):
        """Calculate SHA256 hash of file"""
        sha256 = hashlib.sha256()

        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256.update(chunk)

        return sha256.hexdigest()

    def _cleanup_old_versions(self, base_filename):
        """Keep only the most recent N versions"""
        versions = []

        # Find all versions
        for file_name in os.listdir(self.version_dir):
            if file_name.startswith(base_filename) and not file_name.endswith('.json'):
                file_path = os.path.join(self.version_dir, file_name)
                versions.append((file_name, os.path.getctime(file_path)))

        # Sort by creation time (newest first)
        versions.sort(key=lambda x: x[1], reverse=True)

        # Delete old versions
        for file_name, _ in versions[self.max_versions:]:
            version_path = os.path.join(self.version_dir, file_name)
            meta_path = f"{version_path}.json"

            os.remove(version_path)
            if os.path.exists(meta_path):
                os.remove(meta_path)

            print(f"🗑️  Removed old version: {file_name}")


def main():
    """Example usage and CLI"""
    print("=" * 80)
    print("DocuFlow - Version Control")
    print("=" * 80)

    vc = VersionControl()

    print("\nAvailable commands:")
    print("1. Create version")
    print("2. List versions")
    print("3. Restore version")
    print("4. Compare versions")
    print("5. View version history")

    choice = input("\nEnter choice (1-5): ").strip()

    if choice == "1":
        file_path = input("File path: ").strip()
        comment = input("Comment (optional): ").strip()
        vc.create_version(file_path, comment)

    elif choice == "2":
        base_name = input("Base filename: ").strip()
        versions = vc.list_versions(base_name)

        print(f"\n📋 Found {len(versions)} version(s):")
        for v in versions:
            print(f"\n  {v['filename']}")
            print(f"    Created: {v['created'].strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"    Size: {v['size']:,} bytes")
            if 'comment' in v:
                print(f"    Comment: {v['comment']}")

    elif choice == "3":
        version_path = input("Version path: ").strip()
        destination = input("Restore to: ").strip()
        vc.restore_version(version_path, destination)

    elif choice == "4":
        v1 = input("Version 1 path: ").strip()
        v2 = input("Version 2 path: ").strip()
        result = vc.compare_versions(v1, v2)

        if result:
            print(f"\n📊 Comparison:")
            print(f"  Identical: {result['identical']}")
            print(f"  Size difference: {result['size_diff']:,} bytes")

    elif choice == "5":
        base_name = input("Base filename: ").strip()
        limit = input("Max versions to show (or blank for all): ").strip()
        limit = int(limit) if limit else None

        history = vc.get_version_history(base_name, limit)

        print(f"\n📜 Version History ({len(history)} versions):")
        for i, v in enumerate(history, 1):
            print(f"\n{i}. {v['filename']}")
            print(f"   Created: {v['created'].strftime('%Y-%m-%d %H:%M:%S')}")
            if 'comment' in v:
                print(f"   Comment: {v['comment']}")


if __name__ == "__main__":
    main()
