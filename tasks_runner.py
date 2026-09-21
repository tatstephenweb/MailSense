import os
from dotenv import load_dotenv
load_dotenv()

from flask import Flask
import db_handler
from scheduler import get_user_tokens, generate_new_access_token
from decoding_email import poll_new_emails, fetch_and_decode_bodies

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
        print('run after 5 secs')
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
        except Exception as e:
            print(f'{e}: unable to get access tokens and poll this user: {user_id}. {email}')
            continue #move to the next user even when there is an error on this user get tokens and poll

scheduler.add_job(func=run_all_users, trigger='interval', minutes=2, id='runallusers')

if __name__ == '__main__':
    scheduler.start()