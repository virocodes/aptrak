import sqlite3
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

DATABASE_NAME = 'app.db'

def connect_db():
    return sqlite3.connect(DATABASE_NAME)

def add_user(username, password, email):
    connection = connect_db()
    cursor = connection.cursor()
    hashed_pwd = generate_password_hash(password, method='pbkdf2:sha256')
    cursor.execute('''
    INSERT INTO users (username, password, email)
    VALUES (?, ?, ?)
    ''', (username, hashed_pwd, email))
    connection.commit()
    connection.close()

def get_user_by_name(username):
    connection = connect_db()
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
    user = cursor.fetchone()
    connection.close()
    return user

def add_application(user_id, job_title, company, status, link="", description=""):
    connection = connect_db()
    cursor = connection.cursor()
    cursor.execute('''
    INSERT INTO applications (user_id, job_title, company, status, applied_on, link, description)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (user_id, job_title, company, status, datetime.now().strftime('%Y-%m-%d'), link, description))
    connection.commit()
    connection.close()

def get_applications_by_user(user_id):
    connection = connect_db()
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM applications WHERE user_id = ?', (user_id,))
    applications = cursor.fetchall()
    connection.close()
    return applications

def get_application_by_id(application_id):
    connection = connect_db()
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM applications WHERE id = ?', (application_id,))
    application = cursor.fetchone()
    connection.close()
    return application

def delete_application_by_id(application_id, user_id):
    connection = connect_db()
    cursor = connection.cursor()
    cursor.execute('DELETE FROM applications WHERE id = ? AND user_id = ?', (application_id, user_id))
    connection.commit()
    connection.close()

def update_application_by_id(application_id, user_id, field, value):
    connection = connect_db()
    cursor = connection.cursor()
    cursor.execute(f'UPDATE applications SET {field} = ? WHERE id = ? AND user_id = ?', (value, application_id, user_id))
    connection.commit()
    connection.close()

def create_db():
    connection = sqlite3.connect('job_tracker.db')
    cursor = connection.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS applications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        job_title TEXT NOT NULL,
        company TEXT NOT NULL,
        status TEXT NOT NULL,
        applied_on DATE NOT NULL,
        link TEXT,
        description MEDIUMTEXT,
        notes MEDIUMTEXT,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    ''')

    connection.commit()
    connection.close()

create_db()

