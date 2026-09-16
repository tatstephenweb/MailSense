from datetime import datetime
import sqlite3 as sqlite

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
                    last_synced_at DATETIME,
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
                    email_id TEXT NOT NULL UNIQUE,
                    subject TEXT,
                    sender TEXT,
                    snippet TEXT,
                    priority TEXT,
                    status TEXT,
                    deadline DATETIME,
                    received_at DATETIME,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            ''')
            conn.commit()
            print("Table 'emails' created successfully.")
        except Exception as e:
            print(f"Error: {e}")
        conn.close()

def insert_email(user_id, email_id, subject, sender, snippet, priority, status, deadline, received_at):
    conn = get_connection("mailsense.db")
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO emails (user_id, email_id, subject, sender, snippet, priority, status, deadline, received_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (user_id, email_id, subject, sender, snippet, priority, status, deadline, received_at))
            conn.commit()
            print(f"Email {email_id} inserted successfully.")
        except Exception as e:
            print(f"Error: {e}")
        conn.close()
        
