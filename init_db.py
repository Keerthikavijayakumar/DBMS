import sqlite3

# Connect to SQLite database
conn = sqlite3.connect('it_company.db')
cur = conn.cursor()

# Create the tables if they do not exist
cur.execute('''
    CREATE TABLE IF NOT EXISTS clients (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT NOT NULL,
        phone TEXT NOT NULL,
        address TEXT,
        company TEXT
    )
''')

cur.execute('''
    CREATE TABLE IF NOT EXISTS projects (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        status TEXT,
        client_id INTEGER,
        start_date DATE,
        end_date DATE,
        FOREIGN KEY (client_id) REFERENCES clients(id)
    )
''')

cur.execute('''
    CREATE TABLE IF NOT EXISTS employees (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        role TEXT NOT NULL,
        email TEXT NOT NULL,
        phone TEXT NOT NULL,
        department TEXT NOT NULL,
        project_id INTEGER,
        FOREIGN KEY (project_id) REFERENCES projects(id)
    )
''')

# Commit and close the connection
conn.commit()
conn.close()
