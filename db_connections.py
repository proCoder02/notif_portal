import psycopg2
import os
import json

def get_connection():
    return psycopg2.connect(
        host="localhost",
        database="notif",
        user="postgres",
        password="0326"
    )

# def fetch_user(username):
#     conn = get_connection()
#     cur = conn.cursor()
#     cur.execute("SELECT username, password, role FROM notif.users WHERE username = %s", (username,))
#     user = cur.fetchone()
#     cur.close()
#     conn.close()
#     return user
def fetch_user(username):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT username, password, role, room_code FROM notif.users WHERE username = %s", (username,))
    result = cur.fetchone()
    cur.close()
    conn.close()
    return result


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


# --- Notifications
# def insert_notification(username, text):
#     with get_connection() as conn:
#         with conn.cursor() as cur:
#             cur.execute("INSERT INTO notif.user_notifications (username, text) VALUES (%s, %s)", (username, text))

# def fetch_notifications(username):
#     with get_connection() as conn:
#         with conn.cursor() as cur:
#             cur.execute("SELECT text, timestamp FROM notif.user_notifications WHERE username = %s ORDER BY timestamp DESC", (username,))
#             return cur.fetchall()
def fetch_notifications(room_code):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT message, timestamp FROM notif.notifications WHERE room_code = %s ORDER BY timestamp DESC", (room_code,))
    results = cur.fetchall()
    cur.close()
    conn.close()
    return results

def insert_notification(room_code, message):
    conn =get_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO notif.notifications (room_code, message) VALUES (%s, %s)", (room_code, message))
    conn.commit()
    cur.close()
    conn.close()
# --- Polls
# def insert_poll(username, question, options, votes):
#     with get_connection() as conn:
#         with conn.cursor() as cur:
#             cur.execute(
#                 "INSERT INTO notif.user_polls (username, question, options, votes) VALUES (%s, %s, %s, %s)",
#                 (username, question, options, json.dumps(votes))
#             )

# def fetch_polls(username):
#     with get_connection() as conn:
#         with conn.cursor() as cur:
#             cur.execute("SELECT id, question, options, votes FROM notif.user_polls WHERE username = %s", (username,))
#             return cur.fetchall()    
#     conn.commit()
#     cur.close()
#     conn.close()
#     return True

def insert_poll(room_code, question, options, votes):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO notif.polls (room_code, question, options, votes) VALUES (%s, %s, %s, %s)",
                (room_code, question, options, json.dumps(votes)))
    conn.commit()
    cur.close()
    conn.close()

def fetch_polls(room_code):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, question, options, votes FROM notif.polls WHERE room_code = %s", (room_code,))
    results = cur.fetchall()
    cur.close()
    conn.close()
    return results