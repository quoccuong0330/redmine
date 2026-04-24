#!/usr/bin/env python3
"""Redmine daily digest — sends HTML email at 5pm Mon-Fri via cron."""

import sys
import logging
from datetime import datetime
from dotenv import load_dotenv
import os

from redmine_client import RedmineClient
from email_renderer import render_digest_email, render_brief_email
from email_sender import EmailSender

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
)
log = logging.getLogger(__name__)


def main():
    dry_run = '--dry-run' in sys.argv
    brief   = '--brief' in sys.argv

    try:
        redmine_url  = os.environ['REDMINE_URL']
        redmine_user = os.environ['REDMINE_USER']
        redmine_pass = os.environ['REDMINE_PASS']
        smtp_host    = os.environ['SMTP_HOST']
        smtp_port    = int(os.environ['SMTP_PORT'])
        smtp_user    = os.environ['SMTP_USER']
        smtp_pass    = os.environ['SMTP_APP_PASSWORD']
        email_to     = os.environ['EMAIL_TO']
        email_from   = os.environ['EMAIL_FROM']
    except KeyError as e:
        log.error("Missing required env var: %s", e)
        sys.exit(1)

    try:
        log.info("Fetching Redmine data...")
        client = RedmineClient(redmine_url, redmine_user, redmine_pass)
        time_entries = client.get_today_time_entries()

        if brief:
            html = render_brief_email(time_entries, redmine_url)
            now_str = datetime.now().strftime('%H:%M %a %d %b')
            subject = f"⏱ Progress {now_str} — {sum(e.get('hours',0) for e in time_entries):.1f}h logged"
        else:
            due_today    = client.get_issues_due_today()
            due_tomorrow = client.get_issues_due_tomorrow()
            log.info(
                "Data: %d time entries, %d due today, %d due tomorrow",
                len(time_entries), len(due_today), len(due_tomorrow),
            )
            html = render_digest_email(time_entries, due_today, due_tomorrow, redmine_url)
            today_str = datetime.now().strftime('%a %d %b %Y')
            subject = f"📋 Redmine Digest — {today_str}"

        if dry_run:
            log.info("DRY RUN — printing HTML to stdout, no email sent")
            print(html)
            return

        log.info("Sending email to %s...", email_to)
        sender = EmailSender(smtp_host, smtp_port, smtp_user, smtp_pass)
        sender.send(email_from, email_to, subject, html)
        log.info("Email sent successfully")

    except Exception as e:
        log.error("Digest failed: %s", e, exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
