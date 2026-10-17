import os, logging, json
from dotenv import load_dotenv
load_dotenv()

import notifier
from google.cloud import pubsub_v1
from google.oauth2 import service_account
import db_handler
from scheduler import get_user_tokens, generate_new_access_token
from decoding_email import poll_new_emails, fetch_and_decode_bodies
from googleapiclient.discovery import build

logging.basicConfig(level=logging.INFO)


def start_watch(user_id):
    service = generate_new_access_token(user_id)
    body = {
        "topicName" : os.getenv("PUBSUB_TOPIC"),
        "labelIds" : ["INBOX"],
    }
    result = service.users().watch(userId="me", body=body).execute()



def lookup_user_id(email):
    conn = db_handler.get_connection("mailsense.db")
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id FROM users WHERE email = %s", (email,)
    )
    rows = cursor.fetchone()
    conn.close()
    if rows is None:  # user not in our database (for example, deleted)
        return None
    return rows[0]
    

def handle_message(message):
    try:
        data = json.loads(message.data.decode("utf-8"))
        email = data["emailAddress"]
        logging.info("Change notification for %s", email)

        user_id = lookup_user_id(email)
        if user_id is None:
            message.ack()  # not one of our users, drop it
            return

        classified_data = fetch_and_decode_bodies(user_id, poll_new_emails(user_id))
        for cd in classified_data:
            db_handler.insert_email(user_id, cd["subject"], cd["sender"], cd["body"], cd["priority"], cd["reason"])
            #TESTING TO CALL THE SEND PUSH NOTIFICATIONS FUNCTION TO SEND A NOTIFICATION OF A NEWLY HIGH PRIORITIZED MAIL TO THE USER
            if cd['priority'] == 'High':
                notifier.send_push_notification(user_id, cd['subject'], cd['sender'])
                
        message.ack()
    except Exception:
        logging.exception("Failed handling message")
        message.nack()  # Pub/Sub will redeliver it


def make_subscriber():
    # On Railway the service account is stored as JSON text in GOOGLE_SERVICE_ACCOUNT_JSON.
    # Locally it still falls back to GOOGLE_APPLICATION_CREDENTIALS (a file path).
    raw = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")
    if raw:
        creds = service_account.Credentials.from_service_account_info(json.loads(raw))
        return pubsub_v1.SubscriberClient(credentials=creds)
    return pubsub_v1.SubscriberClient()


def main():
    subscriber = make_subscriber()
    sub_path = os.getenv("PUBSUB_SUBSCRIPTION")
    flow = pubsub_v1.types.FlowControl(max_messages=1)
    future = subscriber.subscribe(sub_path, callback=handle_message, flow_control=flow)
    logging.info("Listening on %s", sub_path)
    try:
        future.result()
    except KeyboardInterrupt:
        future.cancel()


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

'''def run_all_users():
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
            
'''

'''scheduler.add_job(func=run_all_users, trigger='interval', seconds=100, id='runallusers')
initially used a timer to run tasks but now uses a pubsub that run tasks immediately the user gets a mail making it faster
'''



if __name__ == '__main__':
   main()
