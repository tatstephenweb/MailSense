import base64
from scheduler import generate_new_access_token
import db_handler
from classifier import classify_email
#Function to decode body of the mail from base64 to plain understandable text

def decode_email_body(payload):

    #if the body is in the payload directly this condition will execute
    if payload.get('body', {}).get('data'):
        data = payload['body']['data']
        return base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')

    #if the email body is divided into parts, this condition will be executed
    if 'parts' in payload:

        # the loop if the body is stored as plain text
        for part in payload['parts']:
            if part.get('mimeType') == 'text/plain' and part.get('body', {}).get('data'):
                data = part['body']['data']
                return base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')

        # the loop if the body is stored as html
        for part in payload['parts']:
            if part.get('mimeType') == 'text/html' and part.get('body', {}).get('data'):
                data = part['body']['data']
                return base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')

    return "" 

multipart_payload = {
    "mimeType": "multipart/alternative",
    "parts": [
        {
            "mimeType": "text/plain",
            "body": {
                "data": "VGhpcyBpcyB0aGUgcGxhaW4gdGV4dCB2ZXJzaW9uIG9mIHRoZSBlbWFpbC4gVXJnZW50OiBwbGVhc2UgcmVzcG9uZCBieSA1cG0u"
            }
        },
        {
            "mimeType": "text/html",
            "body": {
                "data": "PGh0bWw+PGJvZHk+PHA+VGhpcyBpcyB0aGUgSFRNTCB2ZXJzaW9uPC9wPjwvYm9keT48L2h0bWw+"
            }
        }
    ]
}

simple_payload = {
    "mimeType": "text/plain",
    "body": {
        "data": "SGVsbG8gVGF0LCB0aGlzIGlzIGEgc2ltcGxlIHBsYWluIHRleHQgZW1haWwgd2l0aCBubyBIVE1MIHZlcnNpb24u"
    }
}

#this function will get the last history id of the user and store it in the database, this will be used to get the new emails from the user's mailbox
def initialize_sync(user_id):
    service = generate_new_access_token(user_id)  # returns the Gmail API service object
    if not service:
        return None

    profile = service.users().getProfile(userId='me').execute()
    current_history_id = profile['historyId']

    conn = db_handler.get_connection("mailsense.db")
    if conn:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE users SET last_history_id = ? WHERE id = ?",
            (current_history_id, user_id)
        )
        conn.commit()
        conn.close()

    return current_history_id


def poll_new_emails(user_id):
    service = generate_new_access_token(user_id)
    if not service:
        return None

    # Get the last saved historyId for this user
    conn = db_handler.get_connection("mailsense.db")
    cursor = conn.cursor()
    cursor.execute("SELECT last_history_id FROM users WHERE id = ?", (user_id,))
    row = cursor.fetchone()

    if not row or not row[0]:
        conn.close()
        return None  # user hasn't been baselined yet — should call initialize_sync first

    last_history_id = row[0]

    #print(service.users().getProfile(userId='me').execute())

    response = service.users().history().list(
        userId = 'me',
        startHistoryId = last_history_id,
        historyTypes = ['messageAdded']
    ).execute()

    new_message_ids = []
    for event in response.get('history', []):
        for added in event.get('messagesAdded', []):
            new_message_ids.append(added['message']['id'])

    new_history_id = response.get('historyId', last_history_id)
    cursor.execute(
        "UPDATE users SET last_history_id = ? WHERE id = ?",
        (new_history_id, user_id)
    )
    conn.commit()
    conn.close()

    return new_message_ids

def fetch_and_decode_bodies(user_id, message_ids):
    service = generate_new_access_token(user_id)
    if not service:
        return []

    emails = []
    for msg_id in message_ids:
        message = service.users().messages().get(
            userId='me',
            id=msg_id,
            format='full'
        ).execute()

        payload = message['payload']
        body = decode_email_body(payload)

        headers = payload.get('headers', [])
        subject = next((h['value'] for h in headers if h['name'] == 'Subject'), '')
        sender = next((h['value'] for h in headers if h['name'] == 'From'), '')

        classification = classify_email(sender, subject, body)

        emails.append({
            #'message_id': msg_id,
            'sender': sender,
            'subject': subject,
            'body': body,
            'priority': classification['priority'],
            'reason': classification['reason']
        })

    return emails

fetch_body = fetch_and_decode_bodies(1, ['1a0aea0d5d60f3ae'])
print(fetch_body)