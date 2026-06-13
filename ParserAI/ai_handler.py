import os
import logging
import requests
from google import genai

class ParserAIHandler:
    def __init__(self):
        # Ініціалізація повністю безкоштовного Google Gemini API
        self.client = genai.Client()

    def fetch_trending_product(self) -> dict:
        """
        Бойовий парсер трендових знижок.
        """
        try:
            response = requests.get("https://open-up.biz", timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get("items"):
                    item = data["items"]
                    return {
                        "title": item.get("title", "Смарт-гаджет"),
                        "old_price": f"{item.get('old_price', '2500')} UAH",
                        "new_price": f"{item.get('new_price', '1499')} UAH",
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
        Генерація соковитого тексту через безкоштовну модель gemini-2.5-flash
        """
        prompt = f"""
        Ти — найкращий копірайтер для Telegram-каналів з розпродажами. 
        Напиши агресивний, ультра-короткий та закликаючий пост про гарячу знижку:
        Продукт: {product_data['title']}
        Стара ціна: {product_data['old_price']}
        Нова ціна: {product_data['new_price']}
        
        Критерії тексту:
        1. Використовуй емодзі на початку та для списку.
        2. Напиши 2 речення про те, чому цей товар потрібен прямо зараз.
        3. Чітко покажи вигоду в цифрах (Економія!).
        4. Мова: виключно соковита українська без русизмів.
        """
        try:
            response = self.client.models.generate_content(
                model='gemini-2.5-flash',
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
