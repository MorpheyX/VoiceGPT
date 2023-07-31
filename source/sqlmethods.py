import sqlite3

try:
    Session = sqlite3.connect('Aiobot.db', check_same_thread=False)
    cursor = Session.cursor()
    sqlite_select_query = "select sqlite_version();"
    cursor.execute(sqlite_select_query)
    cursor.execute('''
       CREATE TABLE IF NOT EXISTS users(
           user_id integer,
           user_name text,
           user_username text
       )''')
except sqlite3.Error as error:
    print(f"Error when connecting to sqlite: {error}")


def check_user(user_id):
    user_not_exist = cursor.execute(f'SELECT * FROM users WHERE user_id == {user_id}').fetchone()
    if user_not_exist is None:
        return True
    else:
        return False


def put_user(user_id, user_name, user_username):
    params = int(user_id), user_name, user_username
    cursor.execute(f'INSERT INTO users VALUES(?, ?, ?)', params)
    Session.commit()


def fetchall():
    fetchall.users_ids = cursor.execute('SELECT user_id FROM users').fetchall()
    fetchall.quantity = len(fetchall.users_ids)

