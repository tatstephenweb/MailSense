from scheduler import generate_new_access_token
import db_handler
from decoding_email import decode_email_body

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

        emails.append({
            'message_id': msg_id,
            'sender': sender,
            'subject': subject,
            'body': body
        })

    return emails

print(fetch_and_decode_bodies(1, ['1a0aea0d5d60f3ae']))