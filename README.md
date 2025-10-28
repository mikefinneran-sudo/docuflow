# DocuFlow - Document Management System

**Simple and clean document organization for small business clients**

Version 1.0 | Created: October 22, 2025

---

## What is DocuFlow?

DocuFlow is a complete document management system that automates:

- **Document Organization** - Standardized folder structures and file naming
- **Version Control** - Automatic tracking of document changes
- **Retention Policies** - Automated archiving and deletion of old files
- **Smart Alerts** - Notifications before documents are deleted

Perfect for small businesses that need professional document management without enterprise complexity.

---

## Features

###📁 Document Organization
- Automatic folder structure (Finance, HR, Operations, Sales, Legal)
- Standardized file naming (`Client_Project_20251022_v1.docx`)
- Batch file processing
- Quick search across all departments
- Working → Final → Archive workflow

### 📝 Version Control
- Automatic version snapshots when files change
- Keep last 5 versions (configurable)
- Full metadata tracking (who, when, what changed)
- Easy restore to any previous version
- File integrity verification (SHA256 hashing)

### 📦 Retention Policy
- Auto-archive files older than 30 days (configurable)
- Auto-delete files older than 180 days (configurable)
- Compliance reporting
- Mark important files for permanent retention
- Dry-run mode to preview changes

### 🔔 Alert System
- Email/Slack notifications before file deletion
- Weekly retention reports
- Expiration warnings (7 days before deletion)
- Customizable alert thresholds

---

## Quick Start

### 1. Installation

```bash
# Navigate to DocuFlow directory
cd /path/to/DocuFlow

# Install dependencies (if needed)
# No external dependencies required - uses Python standard library!
```

### 2. Configuration

Edit `config.json` to customize for your business:

```json
{
  "client_name": "Your Company Name",
  "base_path": "Documents",

  "retention_policy": {
    "archive_after_days": 30,
    "delete_after_days": 180
  },

  "alerts": {
    "alert_days_before_delete": 7,
    "notification_method": "email",
    "email": {
      "from_email": "alerts@yourcompany.com",
      "to_email": "admin@yourcompany.com",
      "smtp_server": "smtp.gmail.com",
      "smtp_port": 587
    }
  }
}
```

### 3. Initial Setup

```bash
# Run the main DocuFlow interface
python3 docuflow.py

# Choose option 16: Quick setup (new client)
# This creates all folder structures and initializes the system
```

### 4. Start Organizing

Use the main menu to:
- Organize individual files (option 2)
- Batch organize folders (option 3)
- Create versions before major edits (option 6)

---

## Usage Examples

### Organize a New Document

```bash
python3 docuflow.py
# Choose: 2. Organize single file
# File path: /Downloads/invoice.pdf
# Department: Finance
# Category: Working
# Project name: Q4_Invoices

# Result: Documents/Finance/Working/YourCompany_Q4_Invoices_20251022_v1.pdf
```

### Batch Organize Downloads

```bash
python3 docuflow.py
# Choose: 3. Batch organize folder
# Source folder: /Downloads
# Department: Finance

# All PDF, DOCX, XLSX files automatically organized and renamed
```

### Create a Version Before Editing

```bash
python3 docuflow.py
# Choose: 6. Create version
# File path: Documents/Finance/Working/Contract.docx
# Comment: Before client revisions

# Version saved: versions/Contract.docx.20251022_143052
```

### Run Daily Maintenance

```bash
python3 docuflow.py
# Choose: 17. Daily maintenance

# Automatically:
# - Archives files older than 30 days
# - Deletes files older than 180 days
# - Sends alerts for files expiring soon
```

---

## Folder Structure

DocuFlow creates this structure for each department:

```
Documents/
├── Finance/
│   ├── Working/       # Active documents
│   ├── Final/         # Approved/completed documents
│   └── Archive/       # Old documents (auto-deleted after 180 days)
├── HR/
│   ├── Working/
│   ├── Final/
│   └── Archive/
├── Operations/
├── Sales/
└── Legal/

versions/              # Version history for all files
```

---

## File Naming Convention

All files are automatically renamed to:

```
{ClientName}_{ProjectName}_{Date}_v{Version}.{ext}

Examples:
- AcmeCorp_Q4Report_20251022_v1.pdf
- AcmeCorp_Contract_20251022_v2.docx
- AcmeCorp_Presentation_20251022_v1.pptx
```

This ensures:
- Files sort chronologically
- Easy to identify file contents
- Version tracking built-in
- Professional, consistent naming

---

## Retention Policy Details

### How It Works

1. **Working Files** (0-30 days)
   - Stay in `Working` folder
   - Actively edited and used

2. **Archived Files** (30-180 days)
   - Automatically moved to `Archive` folder
   - Still accessible but marked as old
   - Alert sent 7 days before deletion

3. **Deleted Files** (180+ days)
   - Automatically deleted from `Archive`
   - Cannot be recovered (unless backed up externally)

### Mark Important Files for Retention

```bash
python3 retention_policy.py
# Choose: 4. Mark file for retention
# File path: Documents/Finance/Archive/important_contract.pdf

# File will never be auto-deleted
```

---

## Alert System

### Email Alerts

Configure email in `config.json`:

```json
"alerts": {
  "enabled": true,
  "notification_method": "email",
  "email": {
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587,
    "from_email": "docuflow@yourcompany.com",
    "to_email": "admin@yourcompany.com"
  }
}
```

### Slack Alerts

```json
"alerts": {
  "notification_method": "slack",
  "slack": {
    "webhook_url": "https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
  }
}
```

### Test Alerts

```bash
python3 alert_system.py
# Choose: 3. Test email configuration
```

---

## Automation (Set and Forget)

### Schedule Daily Maintenance

**Mac/Linux (cron):**

```bash
# Edit crontab
crontab -e

# Add this line to run daily at 9 AM:
0 9 * * * cd /path/to/DocuFlow && python3 docuflow.py --daily-maintenance
```

**Windows (Task Scheduler):**

1. Open Task Scheduler
2. Create Basic Task
3. Trigger: Daily at 9:00 AM
4. Action: Start a program
   - Program: `python3`
   - Arguments: `C:\path\to\DocuFlow\docuflow.py --daily-maintenance`

---

## Module Reference

### document_organizer.py
Core file organization and management

### version_control.py
File versioning and history tracking

### retention_policy.py
Automated archiving and deletion

### alert_system.py
Email/Slack notifications

### docuflow.py
Main control interface (use this!)

---

## Configuration Reference

### Full config.json Options

```json
{
  "client_name": "Your Company",
  "base_path": "Documents",

  "folder_structure": {
    "departments": ["Finance", "HR", "Operations", "Sales", "Legal"],
    "categories": ["Working", "Final", "Archive"]
  },

  "naming_convention": {
    "pattern": "{client}_{project}_{date}_v{version}.{ext}",
    "date_format": "%Y%m%d",
    "auto_version": true
  },

  "version_control": {
    "enabled": true,
    "version_dir": "versions",
    "max_versions": 5,
    "track_metadata": true
  },

  "retention_policy": {
    "enabled": true,
    "archive_after_days": 30,
    "delete_after_days": 180,
    "run_schedule": "daily"
  },

  "alerts": {
    "enabled": true,
    "alert_days_before_delete": 7,
    "notification_method": "email",
    "email": {
      "smtp_server": "smtp.gmail.com",
      "smtp_port": 587,
      "from_email": "alerts@company.com",
      "to_email": "admin@company.com"
    }
  },

  "file_types": {
    "documents": [".docx", ".doc", ".pdf", ".txt"],
    "spreadsheets": [".xlsx", ".xls", ".csv"],
    "presentations": [".pptx", ".ppt"],
    "images": [".png", ".jpg", ".jpeg"],
    "archives": [".zip", ".rar"]
  }
}
```

---

## FAQ

**Q: Can I change the retention periods?**
A: Yes! Edit `config.json` and update `archive_after_days` and `delete_after_days`.

**Q: What happens if I delete a file by accident?**
A: If version control is enabled, you can restore from `versions/` folder. Otherwise, use your system backup.

**Q: Can I add custom departments?**
A: Yes! Edit the `departments` array in `config.json` and run setup again.

**Q: Does this work on Windows/Mac/Linux?**
A: Yes! Pure Python with no external dependencies.

**Q: Can multiple people use the same document folder?**
A: Yes, but only one person should run the automated tasks. Consider network drive setup.

**Q: How much disk space do versions use?**
A: Each version is a full copy. With `max_versions: 5`, you'll use ~5x the space of the original file. Adjust as needed.

---

## Troubleshooting

### "Email alerts not working"

1. Check SMTP credentials in `config.json`
2. Enable "Less secure apps" for Gmail (or use App Password)
3. Test with: `python3 alert_system.py` → option 3

### "Files not being archived"

1. Run dry run first: `python3 docuflow.py` → option 10
2. Check file modification dates (not creation dates)
3. Verify `archive_after_days` setting in config

### "Can't find organized files"

1. Use search: `python3 docuflow.py` → option 5
2. Check all departments: option 4
3. Look in `Archive` folder if file is old

---

## Support

For questions or issues:
- Email: mike.finneran@gmail.com
- Documentation: This README
- Configuration: See `config.json`

---

## License

Copyright 2025 - For use by licensed clients only

---

**DocuFlow** - Professional document management made simple.
