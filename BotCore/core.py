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
    """ГОЛОВНИЙ ОРКЕСТРАТОР: Публікує тільки унікальний контент з коректною асинхронністю."""
    channel_id = os.getenv("CHANNEL_ID")
    subs_count = await marketing_hub.check_channel_subscribers(bot)
    
    logging.info("⚙️ Контент: Початок пошуку унікального товару...")
    
    try:
        # ВИПРАВЛЕНО: Додано обов'язкове слово await для асинхронного запиту
        product = await ai_handler.fetch_trending_product(bot, channel_id)
        ai_text = ai_handler.generate_ai_post(product)
        affiliate_url = pay_manager.generate_affiliate_link(product["raw_url"])
        
        full_caption = f"{ai_text}\n\n🔗 [КУПИТИ ЗІ ЗНИЖКОЮ]({affiliate_url})"
        
        await bot.send_photo(chat_id=channel_id, photo=product["image_url"], caption=full_caption, parse_mode="Markdown")
        logging.info("✅ Унікальний товар успішно надіслано в Telegram-канал.")
    except Exception as e:
        logging.error(f"Помилка під час виконання циклу публікації: {e}")

    # Блок маркетингу для старту
    if subs_count < 500:
        logging.info("⚠️ Режим стартового розвитку: додаємо вірусну рекламу...")
        viral_text = marketing_hub.generate_viral_invite()
        try:
            await bot.send_message(chat_id=channel_id, text=viral_text, parse_mode="Markdown")
        except Exception as e:
            logging.error(f"Помилка маркетингу: {e}")
        await marketing_hub.execute_smart_vp(bot, subs_count)

async def passive_large_marketing_job():
    subs_count = await marketing_hub.check_channel_subscribers(bot)
    if subs_count >= 500:
        await marketing_hub.execute_smart_vp(bot, subs_count)

async def on_startup():
    logging.info("🔥 МИТТЄВИЙ СТАРТ: Публікація першого унікального поста...")
    try:
        await dynamic_orchestrator_job()
    except Exception as e:
        logging.error(f"Помилка миттєвого старту: {e}")

    # Налаштування таймерів на майбутнє
    scheduler.add_job(dynamic_orchestrator_job, 'interval', hours=2)
    scheduler.add_job(passive_large_marketing_job, 'interval', days=3)
    scheduler.start()
    logging.info("🚀 Усі інтервали постів успішно активовані.")

async def start_bot():
    logging.info("🤖 Ініціалізація підключення контент-бота до Telegram...")
    dp.startup.register(on_startup)
    await dp.start_polling(bot)
