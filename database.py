import sqlite3

def init_db():
    conn = sqlite3.connect("skillswap.db")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS profiles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            teach_skill TEXT NOT NULL,
            learn_skill TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            profile_id INTEGER NOT NULL,
            requester_name TEXT NOT NULL,
            message TEXT,
            status TEXT DEFAULT 'Pending',
            FOREIGN KEY (profile_id) REFERENCES profiles(id)
        )
    """)

    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    print("Database initialized successfully!")