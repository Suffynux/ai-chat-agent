import sqlite3

def init_db():
    # Initialize the SQLite database and create necessary tables
    conn = sqlite3.connect('chat.db')
    cursor = conn.cursor()
    
    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            google_id TEXT UNIQUE,
            email TEXT,
            name TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Messages table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_email TEXT,
            role TEXT,
            content TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Daily message count table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS daily_counts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_email TEXT,
            date TEXT,
            count INTEGER DEFAULT 0
        )
    ''')
    
    # Integration settings table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS integrations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_email TEXT UNIQUE,
            whatsapp_number TEXT,
            whatsapp_api_key TEXT,
            store_type TEXT,
            store_url TEXT,
            store_api_key TEXT
        )
    ''')
    
    conn.commit()
    conn.close()

# User management functions
def get_message_count(user_email, date):
    conn = sqlite3.connect('chat.db')
    cursor = conn.cursor()
    cursor.execute(
        'SELECT count FROM daily_counts WHERE user_email=? AND date=?',
        (user_email, date)
    )
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else 0

# Message management functions
def increment_message_count(user_email, date):
    conn = sqlite3.connect('chat.db')
    cursor = conn.cursor()
    existing = get_message_count(user_email, date)
    if existing == 0:
        cursor.execute(
            'INSERT INTO daily_counts (user_email, date, count) VALUES (?, ?, 1)',
            (user_email, date)
        )
    else:
        cursor.execute(
            'UPDATE daily_counts SET count=count+1 WHERE user_email=? AND date=?',
            (user_email, date)
        )
    conn.commit()
    conn.close()

def save_message(user_email, role, content):
    conn = sqlite3.connect('chat.db')
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO messages (user_email, role, content) VALUES (?, ?, ?)',
        (user_email, role, content)
    )
    conn.commit()
    conn.close()

def get_history(user_email, limit=20):
    conn = sqlite3.connect('chat.db')
    cursor = conn.cursor()
    cursor.execute(
        'SELECT role, content FROM messages WHERE user_email=? ORDER BY timestamp DESC LIMIT ?',
        (user_email, limit)
    )
    rows = cursor.fetchall()
    conn.close()
    return [{"role": r[0], "content": r[1]} for r in reversed(rows)]

def save_integration(user_email, data):
    conn = sqlite3.connect('chat.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO integrations (user_email, whatsapp_number, whatsapp_api_key, store_type, store_url, store_api_key)
        VALUES (?, ?, ?, ?, ?, ?)
        ON CONFLICT(user_email) DO UPDATE SET
            whatsapp_number=excluded.whatsapp_number,
            whatsapp_api_key=excluded.whatsapp_api_key,
            store_type=excluded.store_type,
            store_url=excluded.store_url,
            store_api_key=excluded.store_api_key
    ''', (
        user_email,
        data.get('whatsapp_number', ''),
        data.get('whatsapp_api_key', ''),
        data.get('store_type', ''),
        data.get('store_url', ''),
        data.get('store_api_key', '')
    ))
    conn.commit()
    conn.close()

def get_integration(user_email):
    conn = sqlite3.connect('chat.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM integrations WHERE user_email=?', (user_email,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return {
            "whatsapp_number": row[2],
            "whatsapp_api_key": row[3],
            "store_type": row[4],
            "store_url": row[5],
            "store_api_key": row[6]
        }
    return {}