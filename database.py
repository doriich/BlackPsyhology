import sqlite3
from datetime import datetime, timedelta
import os

class Database:
    def __init__(self, db_path='users.db'):
        self.db_path = db_path
        self.init_db()
    
    def init_db(self):
        """Initialize the database with required tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_id INTEGER UNIQUE NOT NULL,
                username TEXT,
                first_name TEXT,
                last_name TEXT,
                tokens INTEGER DEFAULT 10,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_access TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create payments table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS payments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                amount REAL NOT NULL,
                tokens INTEGER NOT NULL,
                payment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def get_user(self, telegram_id):
        """Get user by telegram_id"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, telegram_id, username, first_name, last_name, tokens, created_at, last_access
            FROM users WHERE telegram_id = ?
        ''', (telegram_id,))
        
        user = cursor.fetchone()
        conn.close()
        
        if user:
            return {
                'id': user[0],
                'telegram_id': user[1],
                'username': user[2],
                'first_name': user[3],
                'last_name': user[4],
                'tokens': user[5],
                'created_at': user[6],
                'last_access': user[7]
            }
        return None
    
    def create_user(self, telegram_id, username=None, first_name=None, last_name=None):
        """Create a new user"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO users (telegram_id, username, first_name, last_name, tokens)
                VALUES (?, ?, ?, ?, 10)
            ''', (telegram_id, username, first_name, last_name))
            
            conn.commit()
            user_id = cursor.lastrowid
            
            # Get the created user
            cursor.execute('''
                SELECT id, telegram_id, username, first_name, last_name, tokens, created_at, last_access
                FROM users WHERE id = ?
            ''', (user_id,))
            
            user = cursor.fetchone()
            conn.close()
            
            if user:
                return {
                    'id': user[0],
                    'telegram_id': user[1],
                    'username': user[2],
                    'first_name': user[3],
                    'last_name': user[4],
                    'tokens': user[5],
                    'created_at': user[6],
                    'last_access': user[7]
                }
            return None
        except sqlite3.IntegrityError:
            conn.close()
            return None
    
    def update_last_access(self, user_id):
        """Update user's last access time"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE users SET last_access = CURRENT_TIMESTAMP WHERE id = ?
        ''', (user_id,))
        
        conn.commit()
        conn.close()
    
    def use_token(self, user_id):
        """Use one token from user's balance"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE users SET tokens = tokens - 1 WHERE id = ? AND tokens > 0
        ''', (user_id,))
        
        conn.commit()
        rows_affected = cursor.rowcount
        conn.close()
        
        return rows_affected > 0
    
    def add_tokens(self, user_id, tokens):
        """Add tokens to user's balance"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE users SET tokens = tokens + ? WHERE id = ?
        ''', (tokens, user_id))
        
        conn.commit()
        conn.close()
    
    def get_user_token_status(self, user_id):
        """Check if user has tokens and if they're still valid (within 3 days)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT tokens, created_at FROM users WHERE id = ?
        ''', (user_id,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            tokens, created_at = result
            created_date = datetime.fromisoformat(created_at)
            now = datetime.now()
            days_since_creation = (now - created_date).days
            
            return {
                'tokens': tokens,
                'days_remaining': max(0, 3 - days_since_creation),
                'is_active': days_since_creation < 3,
                'has_tokens': tokens > 0
            }
        
        return None
    
    def add_payment(self, user_id, amount, tokens):
        """Record a payment"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO payments (user_id, amount, tokens)
            VALUES (?, ?, ?)
        ''', (user_id, amount, tokens))
        
        conn.commit()
        payment_id = cursor.lastrowid
        conn.close()
        
        return payment_id