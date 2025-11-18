import sys
import os
import sqlite3
from datetime import datetime, timedelta

# Add the current directory to the path so we can import modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import Database
from payment import payment_handler

def test_bot_functionality():
    """Test the bot functionality"""
    print("Testing bot functionality...")
    
    # Initialize database
    db = Database('test_bot.db')
    
    # Test creating a user
    print("Creating test user...")
    user = db.create_user(
        telegram_id=987654321,
        username='bot_tester',
        first_name='Bot',
        last_name='Tester'
    )
    
    if user:
        print(f"User created successfully: {user}")
    else:
        print("Failed to create user")
        return
    
    # Test token status
    print("\nChecking token status...")
    token_status = db.get_user_token_status(user['id'])
    print(f"Token status: {token_status}")
    
    # Test search functionality (using tokens)
    print("\nTesting search functionality...")
    if token_status['is_active'] and token_status['has_tokens']:
        success = db.use_token(user['id'])
        if success:
            print("Token used successfully for search")
        else:
            print("Failed to use token for search")
    else:
        print("Cannot test search - no active tokens or expired trial")
    
    # Test payment functionality
    print("\nTesting payment functionality...")
    payment_info = payment_handler.generate_payment_info(user['id'], 10, 100)
    print("Payment information generated:")
    print(payment_info)
    
    # Test adding tokens through payment
    print("\nTesting token addition through payment...")
    success = payment_handler.process_payment_confirmation(user['id'], 25)
    if success:
        print("Payment processed successfully")
    else:
        print("Failed to process payment")
    
    # Check final token status
    print("\nChecking final token status...")
    final_token_status = db.get_user_token_status(user['id'])
    print(f"Final token status: {final_token_status}")
    
    # Test trial period expiration
    print("\nTesting trial period expiration...")
    # Manually update the user's creation date to simulate expiration
    conn = sqlite3.connect('test_bot.db')
    cursor = conn.cursor()
    
    # Calculate the date 4 days ago to simulate expiration
    expired_date = datetime.now() - timedelta(days=4)
    cursor.execute('''
        UPDATE users SET created_at = ? WHERE id = ?
    ''', (expired_date.isoformat(), user['id']))
    
    conn.commit()
    conn.close()
    
    # Check if user is now expired
    expired_status = db.get_user_token_status(user['id'])
    print(f"Expired user status: {expired_status}")
    print(f"Is user still active: {expired_status['is_active']}")
    
    # Clean up test database
    print("\nCleaning up...")
    os.remove('test_bot.db')
    if os.path.exists('test_bot.db-shm'):
        os.remove('test_bot.db-shm')
    if os.path.exists('test_bot.db-wal'):
        os.remove('test_bot.db-wal')
    
    print("Bot functionality test completed successfully!")

if __name__ == '__main__':
    test_bot_functionality()