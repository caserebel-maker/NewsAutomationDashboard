import sqlite3
import os
from datetime import datetime

DB_PATH = "news_database.db"

def init_db():
    """Initializes the SQLite database and the news_posts table."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS news_posts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        original_title TEXT,
        summary_content TEXT,
        image_path TEXT,
        source_url TEXT,
        status TEXT CHECK(status IN ('pending', 'approved', 'posted', 'rejected')) DEFAULT 'pending',
        scheduled_time DATETIME,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    conn.commit()
    conn.close()

def get_db_connection():
    """Returns a connection to the SQLite database."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def add_news_item(title, summary, image_path, url, status='pending', scheduled_time=None):
    """Adds a new news item to the database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO news_posts (original_title, summary_content, image_path, source_url, status, scheduled_time)
    VALUES (?, ?, ?, ?, ?, ?)
    ''', (title, summary, image_path, url, status, scheduled_time or datetime.now()))
    conn.commit()
    conn.close()

def get_all_news():
    """Fetches all news items from the database, ordered by created_at."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM news_posts ORDER BY created_at DESC')
    rows = cursor.fetchall()
    conn.close()
    return rows

def update_news_item(item_id, title=None, summary=None, status=None):
    """Updates an existing news item in the database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if title:
        cursor.execute('UPDATE news_posts SET original_title = ? WHERE id = ?', (title, item_id))
    if summary:
        cursor.execute('UPDATE news_posts SET summary_content = ? WHERE id = ?', (summary, item_id))
    if status:
        cursor.execute('UPDATE news_posts SET status = ? WHERE id = ?', (status, item_id))
        
    conn.commit()
    conn.close()

def delete_news_item(item_id):
    """Deletes a news item from the database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM news_posts WHERE id = ?', (item_id,))
    conn.commit()
    conn.close()

def get_metrics():
    """Returns counts for total, pending, and posted news items."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT COUNT(*) FROM news_posts')
    total = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM news_posts WHERE status = 'pending'")
    pending = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM news_posts WHERE status = 'posted'")
    posted = cursor.fetchone()[0]
    
    conn.close()
    return total, pending, posted

if __name__ == "__main__":
    init_db()
    print("Database initialized.")
