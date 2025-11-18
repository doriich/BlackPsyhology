import os
from database import Database
from config import ADMIN_CONTACT

class PaymentHandler:
    def __init__(self):
        self.db = Database()
        self.admin_contact = ADMIN_CONTACT
    
    def generate_payment_info(self, user_id, amount, price):
        """
        Generate payment information for the user
        
        Args:
            user_id (int): User ID
            amount (int): Number of tokens
            price (int): Price in RUB
            
        Returns:
            str: Payment information message
        """
        # In a real implementation, this would integrate with a payment system
        # For now, we'll provide instructions for manual payment
        
        payment_message = f"""
Оплата {price} рублей за {amount} токенов.

Для оплаты переведите деньги на карту:
**** **** **** **** (Карта скрыта для безопасности)

После оплаты свяжитесь с администратором {self.admin_contact} для подтверждения и пополнения баланса.

Идентификатор платежа: PAY-{user_id}-{amount}-{price}
Пожалуйста, укажите этот идентификатор при обращении к администратору.
        """
        
        return payment_message
    
    def process_payment_confirmation(self, user_id, amount, transaction_id=None):
        """
        Process payment confirmation and add tokens to user
        
        Args:
            user_id (int): User ID
            amount (int): Number of tokens
            transaction_id (str, optional): Transaction ID
            
        Returns:
            bool: True if successful, False otherwise
        """
        # In a real implementation, this would verify the payment
        # For now, we'll just add the tokens to the user's account
        
        try:
            # Add tokens to user
            self.db.add_tokens(user_id, amount)
            
            # Record payment
            self.db.add_payment(user_id, amount * 10, amount)  # 10 RUB per token
            
            return True
        except Exception as e:
            print(f"Error processing payment: {e}")
            return False
    
    def get_payment_options(self):
        """
        Get available payment options
        
        Returns:
            dict: Payment options with amount and price
        """
        return {
            '10_tokens': {'amount': 10, 'price': 100},
            '25_tokens': {'amount': 25, 'price': 250},
            '50_tokens': {'amount': 50, 'price': 500},
            '100_tokens': {'amount': 100, 'price': 1000}
        }

# Singleton instance
payment_handler = PaymentHandler()