from dotenv import load_dotenv
from flask import jsonify, request
load_dotenv()
import authenticate  # Import authentication module
from authenticate import app, Flask, url_for, session, render_template, redirect, oauth
import sqlite3 as sqlite
import db_handler
from crypto import decrypt_text

@app.route("/")
def home():
    return render_template("mailsense.html")

@app.route('/login')
def login():
    redirect_uri = url_for('auth', _external=True)
    return oauth.google.authorize_redirect(redirect_uri, access_type='offline', prompt='consent')

@app.route('/auth/callback')
def auth():
    token = oauth.google.authorize_access_token()
    session['user'] = token['userinfo']

    google_sub = token['userinfo']['sub']
    email = token['userinfo']['email']
    name = token['userinfo']['name']
    picture_url = token['userinfo']['picture']
    access_token = token['access_token']
    refresh_token = token.get('refresh_token')  # Use .get() to avoid KeyError if refresh_token is not present
    token_expiry = token['expires_at']

    print(google_sub, email, name, picture_url, access_token, refresh_token, token_expiry)

    # Insert or update user in the database
    user_id = db_handler.insert_user(
        google_sub, email, name, picture_url, access_token, refresh_token, token_expiry
    )

    session['user_id'] = user_id
    return redirect(url_for('dashboard'))

@app.route('/logout')
def logout():
    session.pop('user', None)
    session.pop('user_id', None)
    return redirect('/')  # Redirect to the dashboard after logout


@app.route("/dashboard")
def dashboard():
    return render_template("index.html", name = session['user']['name'], email = session['user']['email'], picture_url = session['user']['picture'] or url_for('static', filename='default-image.png'))

#TO GET EMAILS FROM THE DATABASE
@app.route("/emails")
def get_emails():
    priority = request.args.get('priority', 'all')

    query = "SELECT * FROM emails WHERE user_id = ?"
    params = (session['user_id'],)

    if priority != 'all':
        query += " AND priority = ?"
        params += (priority,)

    query += " ORDER BY created_at DESC"

    conn = db_handler.get_connection("mailsense.db")
    if conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        emails = cursor.fetchall()
        conn.close()

    result = []
    for email in emails:
        result.append({
            'id': email[0],
            'user_id': email[1],
            'subject': decrypt_text(email[2]),
            'sender': decrypt_text(email[3]),
            'snippet': decrypt_text(email[4]),
            'priority': email[5],
            'status': email[6],
            'created_at': email[9]
        })
    print(result)

    return jsonify({'priority': priority, 'emails': result})

@app.route('/emails/<int:id>')
def get_email_detail(id):
    query = "SELECT * FROM emails WHERE id = ?"
    params = (id,)
    
    conn = db_handler.get_connection("mailsense.db")
    if conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        emails = cursor.fetchall()
        conn.close()

    if not emails:
        return jsonify({'error': 'Email content not found'}), 404

    result = []
    for email in emails:
        result.append({
            'id': email[0],
            'user_id': email[1],
            #'email_id': email[2],
            'subject': decrypt_text(email[2]),
            'sender': decrypt_text(email[3]),
            'snippet': decrypt_text(email[4]),
            'priority': email[5],
            'status': email[6],
            'recieved_at': email[9]
        })

    return jsonify({
        'emails': result
    })


if __name__ == "__main__":
    db_handler.create_users_table()  # Ensure the users table is created before running the app
    db_handler.create_emails_table()  # Ensure the emails table is created before running the app
    app.run()