from datetime import datetime
import sqlite3 as sqlite
from crypto import encrypt_text
import requests, scheduler

#Datebase creation with SQLite
def get_connection(db_name):
    try:
        return sqlite.connect(db_name)
    except Exception as e:
        print(f"Error: {e}")
        return None


def create_users_table():
    conn = get_connection("mailsense.db")
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email TEXT NOT NULL UNIQUE,
                    name TEXT NOT NULL,
                    google_sub TEXT NOT NULL UNIQUE,
                    picture_url TEXT,
                    access_token TEXT,
                    refresh_token TEXT,
                    token_expiry DATETIME,
                    last_history_id TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            conn.commit()
            print("Table 'users' created successfully.")
        except Exception as e:
            print(f"Error: {e}")
        conn.close()

def insert_user(google_sub, email, name, picture_url, access_token, refresh_token, token_expiry):
    conn = get_connection("mailsense.db")
    if conn:
        cursor = conn.cursor()
        try:
            account_exists_query = "SELECT * FROM users WHERE google_sub = ?"
            account_exists = cursor.execute(account_exists_query, (google_sub,)).fetchone()
            if account_exists: #CHECK IF THE USER ALREADY EXIXTS IN THE DATABASE
                print(f"User with Google sub {google_sub} already exists.")
                #Updating the existing user's tokens and expiry
                if refresh_token:
                    cursor.execute("UPDATE users SET access_token = ?, refresh_token = ?, token_expiry = ? WHERE google_sub = ?",
                                (access_token, refresh_token, token_expiry, google_sub))
                else:
                    cursor.execute("UPDATE users SET access_token = ?, token_expiry = ? WHERE google_sub = ?",
                                (access_token, token_expiry, google_sub))

                conn.commit()
                user_id = account_exists[0]

            else:
                #Inserting a new user into the database if he does not exist
                cursor.execute('''
                    INSERT INTO users (google_sub, email, name, picture_url, access_token, refresh_token, token_expiry)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (google_sub, email, name, picture_url, access_token, refresh_token, token_expiry))
                conn.commit()
                user_id = cursor.lastrowid
                print (user_id)
                print(f"User {email} inserted successfully.")

        except Exception as e:
            print(f"Error: {e}")
        conn.close()

    return user_id

def create_emails_table():
    conn = get_connection("mailsense.db")
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS emails (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    subject TEXT,
                    sender TEXT,
                    snippet TEXT,
                    priority TEXT,
                    reason TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            ''')
            conn.commit()
            print("Table 'emails' created successfully.")
        except Exception as e:
            print(f"Error: {e}")
        conn.close()

def insert_email(user_id, subject, sender, snippet, priority, reason):
    
    result = encrypt_text(sender, subject, snippet)
    
    conn = get_connection("mailsense.db")
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO emails (user_id, subject, sender, snippet, priority, reason)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (user_id, result[1], result[0], result[2], priority, reason))
            conn.commit()
            print(f"Email inserted successfully.")
        except Exception as e:
            print(f"Error: {e}")
        conn.close()

# create push notifications table for storing notifications to send to users
def create_push_subscriptions_table():
    conn = get_connection('mailsense.db')
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS push_subscriptions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            endpoint TEXT NOT NULL UNIQUE,
            encryption_key TEXT NOT NULL,
            auth_key TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    """)
    conn.commit()
    conn.close()

def save_push_subscription(user_id, endpoint, encryption_key, auth_key):
    conn = get_connection("mailsense.db")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO push_subscriptions (user_id, endpoint, encryption_key, auth_key)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(endpoint) DO UPDATE SET
            encryption_key = excluded.encryption_key,
            auth_key = excluded.auth_key
    """, (user_id, endpoint, encryption_key, auth_key))
    print('inserted success')
    conn.commit()
    conn.close()


def get_push_subscriptions(user_id):
    conn = get_connection("mailsense.db")
    cursor = conn.cursor()
    cursor.execute(
        "SELECT endpoint, encryption_key, auth_key FROM push_subscriptions WHERE user_id = ?",
        (user_id,)
    )
    rows = cursor.fetchall()
    conn.close()
    return rows


def delete_push_subscription(endpoint):
    conn = get_connection("mailsense.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM push_subscriptions WHERE endpoint = ?", (endpoint,))
    conn.commit()
    conn.close()


#get all active high priority emails from the database
def get_active_high_emails():
    conn = get_connection("mailsense.db")
    try:
        cur = conn.cursor()
        cur.execute(
            "SELECT id, user_id, sender, subject FROM emails WHERE priority = 'High' "
        )
        return cur.fetchall()
    finally:
        conn.close()

def revoke_user_access(user_id):
    tokens = scheduler.get_user_tokens(user_id)
    token = tokens[1]  # revoking the refresh token kills the access token too

    resp = requests.post(
        "https://oauth2.googleapis.com/revoke",
        params={"token": token},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        timeout=10,
    )

    TABLES = {
        'users': 'id',
        'emails': 'user_id',
        'push_subscriptions': 'user_id',
    }

    conn = get_connection('mailsense.db')
    try:
        cursor = conn.cursor()
        for table, column in TABLES.items():
            cursor.execute(f"DELETE FROM {table} WHERE {column} = ?", (user_id,))
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


    return resp.status_code == 200

#if __name__ == "__main__":
