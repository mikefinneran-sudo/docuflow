#!/usr/bin/env python3
"""
DocuFlow - Alert System Module
Automated notifications for document disposal and policy compliance
"""

import os
import json
import smtplib
from email.message import EmailMessage
from datetime import datetime
from retention_policy import RetentionPolicy


class AlertSystem:
    """Document alert and notification system"""

    def __init__(self, config_path="config.json"):
        """Initialize alert system"""
        with open(config_path, 'r') as f:
            self.config = json.load(f)

        self.alerts_config = self.config['alerts']
        self.retention = RetentionPolicy(config_path)
        self.alert_days = self.alerts_config['alert_days_before_delete']
        self.notification_method = self.alerts_config['notification_method']

    def check_and_alert(self):
        """
        Check for files nearing deletion and send alerts

        Returns:
            Number of alerts sent
        """
        # Get files expiring soon
        expiring_files = self.retention.get_expiring_soon(self.alert_days)

        if not expiring_files:
            print("✅ No files nearing deletion")
            return 0

        # Group by department
        by_department = {}
        for file_info in expiring_files:
            dept = file_info['department']
            if dept not in by_department:
                by_department[dept] = []
            by_department[dept].append(file_info)

        # Send alerts
        alerts_sent = 0

        if self.notification_method == "email":
            alerts_sent = self._send_email_alerts(by_department)
        elif self.notification_method == "slack":
            alerts_sent = self._send_slack_alerts(by_department)
        elif self.notification_method == "console":
            alerts_sent = self._console_alerts(by_department)
        else:
            print(f"⚠️  Unknown notification method: {self.notification_method}")

        return alerts_sent

    def _send_email_alerts(self, by_department):
        """Send email alerts for expiring documents"""
        if not self.alerts_config.get('enabled', True):
            print("⚠️  Alerts are disabled in config")
            return 0

        email_config = self.alerts_config.get('email', {})

        if not all([email_config.get('smtp_server'),
                   email_config.get('from_email'),
                   email_config.get('to_email')]):
            print("❌ Email configuration incomplete")
            return 0

        try:
            # Create email message
            msg = EmailMessage()
            msg['Subject'] = f"DocuFlow Alert: {len(sum(by_department.values(), []))} Documents Expiring Soon"
            msg['From'] = email_config['from_email']
            msg['To'] = email_config['to_email']

            # Build email body
            body = self._build_email_body(by_department)
            msg.set_content(body)

            # Send email
            with smtplib.SMTP(email_config['smtp_server'], email_config.get('smtp_port', 587)) as smtp:
                smtp.starttls()

                # If credentials are provided
                if email_config.get('username') and email_config.get('password'):
                    smtp.login(email_config['username'], email_config['password'])

                smtp.send_message(msg)

            print(f"📧 Email alert sent to {email_config['to_email']}")
            return 1

        except Exception as e:
            print(f"❌ Failed to send email: {e}")
            return 0

    def _send_slack_alerts(self, by_department):
        """Send Slack alerts for expiring documents"""
        import urllib.request
        import urllib.parse

        webhook_url = self.alerts_config.get('slack', {}).get('webhook_url')

        if not webhook_url:
            print("❌ Slack webhook URL not configured")
            return 0

        # Build message
        total_files = sum(len(files) for files in by_department.values())
        message = {
            "text": f"⚠️ *DocuFlow Alert*: {total_files} documents expiring soon",
            "blocks": []
        }

        # Header
        message["blocks"].append({
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": f"📋 {total_files} Documents Nearing Deletion"
            }
        })

        # Details by department
        for dept, files in by_department.items():
            file_list = "\n".join([
                f"• *{f['name']}* - {f['days_until_deletion']} days"
                for f in files[:10]  # Limit to 10 per department
            ])

            message["blocks"].append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*{dept}* ({len(files)} files)\n{file_list}"
                }
            })

        # Send to Slack
        try:
            data = json.dumps(message).encode('utf-8')
            req = urllib.request.Request(webhook_url, data=data, headers={'Content-Type': 'application/json'})

            with urllib.request.urlopen(req) as response:
                if response.status == 200:
                    print("💬 Slack alert sent successfully")
                    return 1
                else:
                    print(f"❌ Slack error: {response.status}")
                    return 0

        except Exception as e:
            print(f"❌ Failed to send Slack alert: {e}")
            return 0

    def _console_alerts(self, by_department):
        """Display alerts in console"""
        total_files = sum(len(files) for files in by_department.values())

        print("\n" + "=" * 80)
        print(f"⚠️  DOCUMENT DISPOSAL ALERT: {total_files} Files Expiring Soon")
        print("=" * 80)

        for dept, files in by_department.items():
            print(f"\n📁 {dept} ({len(files)} files):")
            for file_info in files:
                print(f"\n  {file_info['name']}")
                print(f"    Days until deletion: {file_info['days_until_deletion']}")
                print(f"    Modified: {file_info['modified'].strftime('%Y-%m-%d')}")
                print(f"    Path: {file_info['path']}")

        print("\n" + "=" * 80)
        print("Action Required: Review these files and mark for retention if needed")
        print("=" * 80 + "\n")

        return 1

    def _build_email_body(self, by_department):
        """Build email body text"""
        total_files = sum(len(files) for files in by_department.values())

        body = f"""
DocuFlow Document Disposal Alert
{'=' * 70}

{total_files} document(s) will be automatically deleted within {self.alert_days} days
unless marked for retention.

"""

        for dept, files in by_department.items():
            body += f"\n{dept} ({len(files)} files):\n"
            body += "-" * 70 + "\n"

            for file_info in files:
                body += f"\n  File: {file_info['name']}\n"
                body += f"  Days until deletion: {file_info['days_until_deletion']}\n"
                body += f"  Modified: {file_info['modified'].strftime('%Y-%m-%d %H:%M')}\n"
                body += f"  Path: {file_info['path']}\n"

        body += f"""
{'=' * 70}

Action Required:
1. Review the files listed above
2. Mark important files for retention using the retention policy tool
3. Allow unneeded files to be deleted automatically

This is an automated alert from DocuFlow.
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""

        return body

    def schedule_daily_check(self):
        """
        Schedule daily alert checks

        Note: This is a demonstration. For production, use:
        - cron (Linux/Mac)
        - Task Scheduler (Windows)
        - Or a scheduler library like schedule or APScheduler
        """
        import time

        print("📅 Daily alert check scheduled")
        print("   (This is a demo - use cron/Task Scheduler in production)")

        while True:
            # Check at 9 AM daily
            now = datetime.now()
            if now.hour == 9 and now.minute == 0:
                print(f"\n🔔 Running scheduled alert check - {now.strftime('%Y-%m-%d %H:%M')}")
                self.check_and_alert()

                # Sleep for 1 minute to avoid multiple triggers
                time.sleep(60)
            else:
                # Check every minute
                time.sleep(60)

    def send_retention_report(self):
        """Send comprehensive retention report via email"""
        report = self.retention.get_retention_report()

        # Build report email
        subject = f"DocuFlow Retention Report - {datetime.now().strftime('%Y-%m-%d')}"
        body = self._build_report_email(report)

        if self.notification_method == "email":
            return self._send_report_email(subject, body)
        else:
            print(body)
            return True

    def _build_report_email(self, report):
        """Build retention report email body"""
        body = f"""
DocuFlow Retention Policy Report
{'=' * 70}

Generated: {report['generated_at']}

Policy Settings:
  Archive after: {report['policy']['archive_after_days']} days
  Delete after: {report['policy']['delete_after_days']} days

"""

        for dept, stats in report['departments'].items():
            body += f"\n{dept}:\n"
            body += "-" * 70 + "\n"
            body += f"  Working: {stats['working']['count']} files ({stats['working']['total_size']:,} bytes)\n"
            body += f"    Ready to archive: {stats['working']['old_files']}\n"
            body += f"  Archive: {stats['archive']['count']} files ({stats['archive']['total_size']:,} bytes)\n"
            body += f"    Expiring soon: {stats['archive']['expiring']}\n"
            body += f"  Final: {stats['final']['count']} files ({stats['final']['total_size']:,} bytes)\n"

        body += f"""
{'=' * 70}

This is an automated report from DocuFlow.
"""

        return body

    def _send_report_email(self, subject, body):
        """Send report email"""
        email_config = self.alerts_config.get('email', {})

        try:
            msg = EmailMessage()
            msg['Subject'] = subject
            msg['From'] = email_config['from_email']
            msg['To'] = email_config['to_email']
            msg.set_content(body)

            with smtplib.SMTP(email_config['smtp_server'], email_config.get('smtp_port', 587)) as smtp:
                smtp.starttls()

                if email_config.get('username') and email_config.get('password'):
                    smtp.login(email_config['username'], email_config['password'])

                smtp.send_message(msg)

            print(f"📧 Retention report sent to {email_config['to_email']}")
            return True

        except Exception as e:
            print(f"❌ Failed to send report: {e}")
            return False


def main():
    """Example usage and CLI"""
    print("=" * 80)
    print("DocuFlow - Alert System")
    print("=" * 80)

    alert_system = AlertSystem()

    print("\nAvailable commands:")
    print("1. Check and send alerts now")
    print("2. Send retention report")
    print("3. Test email configuration")
    print("4. Preview alerts (console only)")

    choice = input("\nEnter choice (1-4): ").strip()

    if choice == "1":
        alerts_sent = alert_system.check_and_alert()
        print(f"\n✅ Sent {alerts_sent} alert(s)")

    elif choice == "2":
        alert_system.send_retention_report()

    elif choice == "3":
        # Test email config
        email_config = alert_system.alerts_config.get('email', {})
        print(f"\nEmail Configuration:")
        print(f"  SMTP Server: {email_config.get('smtp_server')}")
        print(f"  SMTP Port: {email_config.get('smtp_port')}")
        print(f"  From: {email_config.get('from_email')}")
        print(f"  To: {email_config.get('to_email')}")

        test = input("\nSend test email? (yes/no): ").strip().lower()
        if test == 'yes':
            try:
                msg = EmailMessage()
                msg['Subject'] = "DocuFlow - Test Email"
                msg['From'] = email_config['from_email']
                msg['To'] = email_config['to_email']
                msg.set_content("This is a test email from DocuFlow alert system.")

                with smtplib.SMTP(email_config['smtp_server'], email_config.get('smtp_port', 587)) as smtp:
                    smtp.starttls()
                    smtp.send_message(msg)

                print("✅ Test email sent successfully")
            except Exception as e:
                print(f"❌ Failed: {e}")

    elif choice == "4":
        # Force console output
        original_method = alert_system.notification_method
        alert_system.notification_method = "console"
        alert_system.check_and_alert()
        alert_system.notification_method = original_method


if __name__ == "__main__":
    main()
