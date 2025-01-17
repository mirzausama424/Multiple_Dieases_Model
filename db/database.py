import sqlite3

db_path = 'user_data.db'

def db_connection():
    connection = sqlite3.connect(db_path, check_same_thread=False)
    return connection

# Function to create the 'users' table if it doesn't exist
def create_users_table():
    connection = db_connection()
    cursor = connection.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            hashed_password TEXT NOT NULL,
            gender TEXT NOT NULL
        )
    """)
    
    connection.commit()
    connection.close()

# Function to create the 'predection' table if it doesn't exist
# def createtable():
#     # Ensure the users table exists before creating the 'predection' and 'history' tables
#     create_users_table()

#     # Get the database connection object
#     connection = db_connection()
#     cursor = connection.cursor()

#     # Creating the 'predection' table if it doesn't already exist
#     cursor.execute("""
#         CREATE TABLE IF NOT EXISTS predection (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             user_id INTEGER,
#             model_name TEXT,
#             features TEXT,
#             prediction TEXT,
#             timestamp TEXT,
#             FOREIGN KEY (user_id) REFERENCES users (id)
#         )
#     """)

#     # Creating the 'history' table if it doesn't already exist
#     cursor.execute("""
#         CREATE TABLE IF NOT EXISTS history (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             user_id INTEGER,
#             model_name TEXT,
#             features TEXT,
#             prediction TEXT,
#             timestamp TEXT,
#             FOREIGN KEY (user_id) REFERENCES users (id)
#         )
#     """)

#     # Committing the changes to the database
#     connection.commit()

#     # Closing the database connection
#     connection.close()

def createtable():
    # Get the database connection object
    connection = db_connection()
    cursor = connection.cursor()

    # Creating the 'predection' table if it doesn't already exist, without 'user_id'
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS predection (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            model_name TEXT,
            features TEXT,
            prediction TEXT,
            timestamp TEXT
        )
    """)

    # Committing the changes to the database
    connection.commit()

    # Closing the database connection
    connection.close()