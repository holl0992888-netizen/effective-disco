import os
import logging
from aiogram import Bot, Dispatcher
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from ParserAI.ai_handler import ParserAIHandler
from MainPay.pay_manager import PayManager
from BotMarketing.marketing_hub import MarketingHub

bot = Bot(token=os.getenv("BOT_TOKEN"))
dp = Dispatcher()
scheduler = AsyncIOScheduler()

ai_handler = ParserAIHandler()
pay_manager = PayManager()
marketing_hub = MarketingHub()

async def dynamic_orchestrator_job():
    """
    ГОЛОВНИЙ ОРКЕСТРАТОР: Контролює стратегію розвитку. 
    На початку життя каналу (<500 підписників) робить рекламу дуже часто.
    """
    channel_id = os.getenv("CHANNEL_ID")
    subs_count = await marketing_hub.check_channel_subscribers(bot)
    
    # 1. ПУБЛІКАЦІЯ КОНТЕНТУ (Кожні 2 години)
    logging.info("⚙️ Генерація автономного контенту через Gemini...")
    product = ai_handler.fetch_trending_product()
    ai_text = ai_handler.generate_ai_post(product)
    affiliate_url = pay_manager.generate_affiliate_link(product["raw_url"])
    
    full_caption = f"{ai_text}\n\n🔗 [КУПИТИ ЗІ ЗНИЖКОЮ]({affiliate_url})"
    try:
        await bot.send_photo(chat_id=channel_id, photo=product["image_url"], caption=full_caption, parse_mode="Markdown")
        logging.info("✅ Товар опубліковано успішно.")
    except Exception as e:
        logging.error(f"Помилка публікації товару: {e}")

    # 2. СТРАТЕГІЯ ШВИДКОГО РОЗВИТКУ
    # Якщо на старті підписників < 500 — реклама запускається АГРЕСИВНО (кожні 2 години разом із постом)
    if subs_count < 500:
        logging.info("⚠️ АКТИВОВАНО РЕЖИМ СТАРТОВОГО РОЗВИТКУ (Часта самореклама)!")
        
        # Публікуємо вірусну інвайт-рекламу
        viral_text = marketing_hub.generate_viral_invite()
        try:
            await bot.send_message(chat_id=channel_id, text=viral_text, parse_mode="Markdown")
            logging.info("✅ Вірусну рекламу додано в канал.")
        except Exception as e:
            logging.error(f"Помилка маркетингу: {e}")
            
        # Запускаємо процес обміну взаємним піаром (ВП)
        await marketing_hub.execute_smart_vp(bot, subs_count)
    else:
        logging.info("ℹ️ Канал перейшов відмітку 500 підписників. Переходимо на стабільний режим реклами.")

async def passive_large_marketing_job():
    """
    Спокійна реклама для вже розвиненого каналу (раз на 3 дні).
    """
    subs_count = await marketing_hub.check_channel_subscribers(bot)
    if subs_count >= 500:
        logging.info("📣 Дозована реклама для великого каналу...")
        await marketing_hub.execute_smart_vp(bot, subs_count)

async def start_bot():
    # Головна лінія: контент + агресивний маркетинг (для старту) кожні 2 години
    scheduler.add_job(dynamic_orchestrator_job, 'interval', hours=2)
    
    # Запасна лінія: спокійна реклама раз на 3 дні (увімкнеться після 500 підписників)
    scheduler.add_job(passive_large_marketing_job, 'interval', days=3)
    
    scheduler.start()
    logging.info("🚀 Бот повністю ініціалізований та готовий до роботи.")
    await dp.start_polling(bot)
