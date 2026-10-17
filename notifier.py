import os
import json
from pywebpush import webpush, WebPushException
import db_handler
from crypto import decrypt_text
from datetime import datetime, timezone
from flask import Flask
from apscheduler.schedulers.blocking import BlockingScheduler

scheduler = BlockingScheduler()


def send_push_notification(user_id, subject, sender):
    subscriptions = db_handler.get_push_subscriptions(user_id)

    payload = json.dumps({
        "title": "High priority email",
        "body": f"{sender}: {subject}"
    })

    for endpoint, encryption_key, auth_key in subscriptions:
        subscription_info = {
            "endpoint": endpoint,
            "keys": {
                "p256dh": encryption_key,
                "auth": auth_key
            }
        }
        try:
            webpush(
                subscription_info=subscription_info,
                data=payload,
                vapid_private_key=os.environ["VAPID_PRIVATE_KEY_PATH"],
                vapid_claims={"sub": os.environ["VAPID_CLAIM_EMAIL"]}
            )
        except WebPushException as ex:
            if ex.response is not None and ex.response.status_code == 410:
                db_handler.delete_push_subscription(endpoint)
            else:
                print(f"Push failed for {endpoint}: {ex}")

def send_high_priority_reminders(): #this function will send reminder high priority mails notifications to users on a regular
    emails = db_handler.get_active_high_emails()
    print(f"Sending reminders for {len(emails)} high priority emails")
    for email in emails:
        try:
            
            sender = decrypt_text(email[2])
            subject = decrypt_text(email[3])
            send_push_notification(
                user_id=email[1],
                subject=subject,
                sender=sender
            )
        except Exception as e:
            print(f"Reminder failed for email {e}")



scheduler.add_job(
    send_high_priority_reminders,
    trigger="cron",
    hour=8,
    minute=3,
    timezone="Africa/Lagos",
    id="high_priority_reminders",
    max_instances=1,
    coalesce=True,
    misfire_grace_time=3600,
)

if __name__ == "__main__":
    scheduler.start()