import sqlite3
from openpyxl import Workbook


def create_table():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Users(
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            name TEXT,
            gender TEXT,
            phone TEXT,
            age INTEGER,
            weight REAL,
            height REAL,
            activity_level INTEGER,
            problem TEXT,
            last_interaction_time TEXT,
            notified INTEGER DEFAULT 0,
            last_bot_message_id INTEGER,
            last_bot_message_type TEXT)''')

    conn.commit()


def export_data_to_xlsx():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    cursor.execute(
        'SELECT user_id, username, name, gender, phone, age, weight, height, activity_level, problem, last_interaction_time, notified FROM Users')
    rows = cursor.fetchall()

    workbook = Workbook()
    sheet = workbook.active

    headers = ['User ID', 'Username', 'Name', 'Gender', 'Phone', 'Age', 'Weight', 'Height', 'Activity Level', 'Problem',
               'Last Interaction Time', 'Notified']
    sheet.append(headers)

    for row in rows:
        sheet.append(row)

    filename = 'users.xlsx'
    workbook.save(filename)

    return filename

