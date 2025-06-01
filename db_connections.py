import psycopg2
import os

def get_connection():
    return psycopg2.connect(
        host="localhost",
        database="notif",
        user="postgres",
        password="0326"
    )

def fetch_user(username):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT username, password, role FROM notif.users WHERE username = %s", (username,))
    user = cur.fetchone()
    cur.close()
    conn.close()
    return user


def create_user(username, password, role):
    conn = psycopg2.connect(
         host="localhost",
        database="notif",
        user="postgres",
        password="0326"
    )
    cur = conn.cursor()

    cur.execute("SELECT * FROM notif.users WHERE username = %s", (username,))
    if cur.fetchone():
        return False  # Username exists

    cur.execute(
        "INSERT INTO notif.users (username, password, role) VALUES (%s, %s, %s)",
        (username, password, role)
    )
    conn.commit()
    cur.close()
    conn.close()
    return True