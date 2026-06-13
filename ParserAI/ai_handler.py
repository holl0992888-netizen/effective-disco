import os
import logging
import requests
from google import genai

# Файл, де бот зберігатиме посилання на вже опубліковані товари
HISTORY_FILE = "posted_products.txt"

class ParserAIHandler:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        self.client = genai.Client(api_key=api_key)

    def _is_already_posted(self, url: str) -> bool:
        """Перевіряє, чи є посилання на товар у журналі історії."""
        if not os.path.exists(HISTORY_FILE):
            return False
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            posted_urls = f.read().splitlines()
        return url in posted_urls

    def _save_to_history(self, url: str):
        """Записує посилання на новий товар у журнал історії."""
        with open(HISTORY_FILE, "a", encoding="utf-8") as f:
            f.write(f"{url}\n")

    def fetch_trending_product(self) -> dict:
        """
        Парсер трендів. Якщо перший товар уже публікувався,
        бот автоматично бере наступний унікальний лот з API.
        """
        try:
            response = requests.get("https://open-up.biz", timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get("items"):
                    # Перебираємо всі товари, які повернуло API
                    for item in data["items"]:
                        product_url = item.get("url", "https://aliexpress.com")
                        
                        # Якщо цей товар ми вже викладали — пропускаємо його
                        if self._is_already_posted(product_url):
                            continue
                        
                        # Якщо товар новий — запам'ятовуємо його і віддаємо в канал
                        self._save_to_history(product_url)
                        return {
                            "title": item.get("title", "Гаджет"),
                            "old_price": f"{item.get('old_price', '1999')} UAH",
                            "new_price": f"{item.get('new_price', '1199')} UAH",
                            "image_url": item.get("image", "https://unsplash.com"),
                            "raw_url": product_url
                        }
        except Exception as e:
            logging.error(f"Помилка парсингу: {e}. Перехід на резерв.")
        
        # Резервний лот (якщо API лежить або всі товари звідти вже опубліковані)
        fallback_url = "https://aliexpress.com"
        if not self._is_already_posted(fallback_url):
            self._save_to_history(fallback_url)
            return {
                "title": "Бездротові Навушники Anker Soundcore P20i Black",
                "old_price": "1499 UAH",
                "new_price": "899 UAH",
                "image_url": "https://unsplash.com",
                "raw_url": fallback_url
            }
        
        # Якщо навіть резервний опубліковано, тимчасово повертаємо його, щоб канал не пустував
        return {
            "title": "Універсальний кабель Baseus Fast Charging USB-C",
            "old_price": "499 UAH",
            "new_price": "299 UAH",
            "image_url": "https://unsplash.com",
            "raw_url": "https://aliexpress.com"
        }

    def generate_ai_post(self, product_data: dict) -> str:
        """Генерація унікального тексту через Gemini 2.5 Flash."""
        prompt = f"""
        Ти — найкращий копірайтер для Telegram-каналів з розпродажами. 
        Напиши агресивний, дуже короткий та закликаючий пост про гарячу знижку:
        Продукт: {product_data['title']}
        Стара ціна: {product_data['old_price']}
        Нова ціна: {product_data['new_price']}
        
        Критерії тексту:
        1. Використи емодзі на початку та для списку переваг.
        2. Напиши 2 речення про те, чому цей товар потрібен прямо зараз.
        3. Чітко покажи вигоду в цифрах (Економиш стільки-то!).
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
                f"⏰ Кількість товару обмежена! Забирай швидше за посиланнями:"
            )
