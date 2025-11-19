class PaymentHandler:
    def generate_payment_info(self, user_id, amount, price):
        return f"""
🧾 Счёт на оплату

ID пользователя: {user_id}
Количество токенов: {amount}
Сумма к оплате: {price} руб.

Для оплаты свяжитесь с администратором: @admin
        """

payment_handler = PaymentHandler()
