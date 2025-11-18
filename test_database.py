import os
import sys
import sqlite3
from datetime import datetime, timedelta

# Add the current directory to the path so we can import the database module
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import Database

def test_database():
    """Test the database functionality"""
    print("Testing database functionality...")
    
    # Initialize database
    db = Database('test_users.db')
    
    # Test creating a user
    print("Creating test user...")
    user = db.create_user(
        telegram_id=123456789,
        username='testuser',
        first_name='Test',
        last_name='User'
    )
    
    if user:
        print(f"User created successfully: {user}")
    else:
        print("Failed to create user")
        return
    
    # Test getting user
    print("\nGetting user...")
    retrieved_user = db.get_user(123456789)
    if retrieved_user:
        print(f"User retrieved: {retrieved_user}")
    else:
        print("Failed to retrieve user")
        return
    
    # Test token status
    print("\nChecking token status...")
    token_status = db.get_user_token_status(user['id'])
    print(f"Token status: {token_status}")
    
    # Test using a token
    print("\nUsing a token...")
    success = db.use_token(user['id'])
    if success:
        print("Token used successfully")
    else:
        print("Failed to use token")
    
    # Check updated token status
    print("\nChecking updated token status...")
    updated_token_status = db.get_user_token_status(user['id'])
    print(f"Updated token status: {updated_token_status}")
    
    # Test adding tokens
    print("\nAdding 5 tokens...")
    db.add_tokens(user['id'], 5)
    
    # Check final token status
    print("\nChecking final token status...")
    final_token_status = db.get_user_token_status(user['id'])
    print(f"Final token status: {final_token_status}")
    
    # Test payment recording
    print("\nRecording payment...")
    payment_id = db.add_payment(user['id'], 100, 10)
    if payment_id:
        print(f"Payment recorded with ID: {payment_id}")
    else:
        print("Failed to record payment")
    
    # Clean up test database
    print("\nCleaning up...")
    os.remove('test_users.db')
    if os.path.exists('test_users.db-shm'):
        os.remove('test_users.db-shm')
    if os.path.exists('test_users.db-wal'):
        os.remove('test_users.db-wal')
    
    print("Database test completed successfully!")

if __name__ == '__main__':
    test_database()