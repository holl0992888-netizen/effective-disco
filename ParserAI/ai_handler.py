import os
import logging
import requests
from google import genai

class ParserAIHandler:
    def __init__(self):
        # Виправлено: явна передача API-ключа з налаштувань хостингу
        api_key = os.getenv("GEMINI_API_KEY")
        self.client = genai.Client(api_key=api_key)

    def fetch_trending_product(self) -> dict:
        """
        Парсер реальних трендових знижок.
        """
        try:
            response = requests.get("https://open-up.biz", timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get("items"):
                    item = data["items"]
                    return {
                        "title": item.get("title", "Гаджет"),
                        "old_price": f"{item.get('old_price', '1999')} UAH",
                        "new_price": f"{item.get('new_price', '1199')} UAH",
                        "image_url": item.get("image", "https://unsplash.com"),
                        "raw_url": item.get("url", "https://aliexpress.com")
                    }
        except Exception as e:
            logging.error(f"Помилка парсингу: {e}. Перехід на резервний лот.")
        
        return {
            "title": "Бездротові Навушники Anker Soundcore P20i Black",
            "old_price": "1499 UAH",
            "new_price": "899 UAH",
            "image_url": "https://unsplash.com",
            "raw_url": "https://aliexpress.com"
        }

    def generate_ai_post(self, product_data: dict) -> str:
        """
        Генерація соковитого тексту через модель gemini-3.5-flash
        """
        prompt = f"""
        Ти — найкращий копірайтер для Telegram-каналів з розпродажами. 
        Напиши агресивний, дуже короткий та закликаючий пост про гарячу знижку:
        Продукт: {product_data['title']}
        Стара ціна: {product_data['old_price']}
        Nova ціна: {product_data['new_price']}
        
        Критерії тексту:
        1. Використи емодзі на початку та для списку переваг.
        2. Напиши 2 речення про те, чому цей товар потрібен прямо зараз.
        3. Чітко покажи вигоду в цифрах (Економія!).
        4. Мова: виключно соковита українська без русизмів.
        """
        try:
            # Виправлено викликальний метод для генерації контенту в новій бібліотеці
            response = self.client.models.generate_content(
                model='gemini-3.5-flash',
                contents=prompt,
            )
            return response.text
        except Exception as e:
            logging.error(f"Збій Gemini API: {e}")
            return (
                f"💥 **ГАРЯЧА ЦІНА: {product_data['title']}**\n\n"
                f"📉 Стара ціна: ~~{product_data['old_price']}~~\n"
                f"💵 Ціна зараз: **{product_data['new_price']}**\n\n"
                f"⏰ Кількість товару обмежена! Забирай швидше за посиланням:"
            )
