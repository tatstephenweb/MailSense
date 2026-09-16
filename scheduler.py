import db_handler
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import os
from datetime import datetime, timezone

from dotenv import load_dotenv
load_dotenv()

#the function returns the access token, refresh token and token expiry for a given user id from the database
#We have to wrap it to a Credentials object to use it with the Gmail API. 

def get_user_tokens(user_id):
    user_id = user_id
    if not user_id:
        return None
    conn = db_handler.get_connection("mailsense.db")
    if conn:
        cursor = conn.cursor()
        cursor.execute("SELECT access_token, refresh_token, token_expiry FROM users WHERE id = ?", (user_id,))
        tokens = cursor.fetchone()
        conn.close()
        return tokens
    return None

#Google needs the user's refresh token, my client id and client secret to generate a new access token. 
# So a function will be created to generate a new access token using the refresh token, client id and client secret.
def generate_new_access_token(user_id):
    tokens = get_user_tokens(user_id)
    if not tokens:
        return None

    #Unpack the tokens
    access_token = tokens[0]
    refresh_token = tokens[1]
    token_expiry = tokens[2]

    print(access_token)
    print(refresh_token)
    print(token_expiry)

    creds = Credentials(
        token=access_token,
        refresh_token=refresh_token,
        expiry=datetime.fromtimestamp(token_expiry, tz=timezone.utc).replace(tzinfo=None),
        token_uri="https://oauth2.googleapis.com/token",
        client_id=os.getenv("GOOGLE_CLIENT_ID"),
        client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    )

    # Refresh the access token if it's expired
    if creds.expired:
        creds.refresh(Request())

        # Convert the refreshed datetime expiry back into a Unix timestamp before saving
        new_expiry = int(creds.expiry.timestamp())
        
        # Update the new access token and expiry in the database
        conn = db_handler.get_connection("mailsense.db")
        if conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE users SET access_token = ?, token_expiry = ? WHERE id = ?",
                (creds.token, new_expiry, user_id),
            )
            conn.commit()
            conn.close()

              # Print the new access token, refresh token, and expiry

    service = build("gmail", "v1", credentials=creds)
    return service

print(generate_new_access_token(1))  # Test the function with a user_id of 1