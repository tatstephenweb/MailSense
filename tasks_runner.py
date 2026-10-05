import os
from dotenv import load_dotenv
load_dotenv()

import notifier
from flask import Flask
import db_handler
from scheduler import get_user_tokens, generate_new_access_token
from decoding_email import poll_new_emails, fetch_and_decode_bodies
from googleapiclient.discovery import build

from apscheduler.schedulers.blocking import BlockingScheduler

scheduler = BlockingScheduler()

def get_all_users():
    conn = db_handler.get_connection("mailsense.db")
    if conn:
        cursor = conn.cursor()
        query = "SELECT * FROM users"
        cursor.execute(query)
        rows = cursor.fetchall()
        conn.close()
        print('running new loop')
        return rows #rows[0] to get the first persons details rows[0][0] to get the first persons index rows[0][1], rows[0][2] etc.
    return []

def run_all_users():
    users = get_all_users()

    for row in users:
        user_id = row[0]
        email = row[1]

        try:
            #generate_new_access_token(user_id)
            #poll_new_emails(user_id)
            classified_data = fetch_and_decode_bodies(user_id, poll_new_emails(user_id))
            for cd in classified_data:
                db_handler.insert_email(user_id, cd["subject"], cd["sender"], cd["body"], cd["priority"], cd["reason"])
                #TESTING TO CALL THE SEND PUSH NOTIFICATIONS FUNCTION TO SEND A NOTIFICATION OF A NEWLY HIGH PRIORITIZED MAIL TO THE USER
                if cd['priority'] == 'High':
                    notifier.send_push_notification(user_id, cd['subject'], cd['sender'])
        except Exception as e:
            print(f'{e}: unable to get access tokens and poll this user: {user_id}. {email}')
            continue #move to the next user even when there is an error on this user get tokens and poll

scheduler.add_job(func=run_all_users, trigger='interval', seconds=100, id='runallusers')

scheduler.add_job(
    notifier.send_high_priority_reminders,
    trigger="cron",
    hour="8",
    minute=0,
    timezone="Africa/Lagos",
    id="high_priority_reminders",
    max_instances=1,
    coalesce=True,
    misfire_grace_time=3600,
)



def start_watch(user_id):
    service = generate_new_access_token(user_id)
    body = {
        "topicName": os.getenv("PUBSUB_TOPIC"),
        "labelIds": ["INBOX"],
    }
    result = service.users().watch(userId="me", body=body).execute()
    print(result)


if __name__ == '__main__':
   start_watch(1)  # use a real user id from your users table