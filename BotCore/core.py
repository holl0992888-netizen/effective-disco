import os
import logging
import asyncio
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
    ГОЛОВНИЙ ОРКЕСТРАТОР: Контролює автономний контент та силу просування.
    """
    channel_id = os.getenv("CHANNEL_ID")
    subs_count = await marketing_hub.check_channel_subscribers(bot)
    
    # 1. ПУБЛІКАЦІЯ КОНТЕНТУ
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

    # 2. СТРАТЕГІЯ ШВИДКОГО РОЗВИТКУ (Якщо підписників менше 500)
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
        logging.info("ℹ️ Канал має понад 500 підписників. Реклама працює в пасивному режимі.")

async def passive_large_marketing_job():
    """
    Спокійна реклама для великого каналу (раз на 3 дні).
    """
    subs_count = await marketing_hub.check_channel_subscribers(bot)
    if subs_count >= 500:
        logging.info("📣 Дозована реклама для великого каналу...")
        await marketing_hub.execute_smart_vp(bot, subs_count)

async def on_startup():
    """
    Ця функція спрацьовує ТОЧНО в момент активації бота.
    """
    logging.info("🔥 МИТТЄВИЙ СТАРТ: Запуск першої публікації без очікування...")
    # Примусово викликаємо першу публікацію та рекламу прямо зараз
    try:
        await dynamic_orchestrator_job()
    except Exception as e:
        logging.error(f"Помилка миттєвого старту: {e}")

    # Налаштовуємо розклад на майбутнє (кожні 2 години та кожні 3 дні)
    scheduler.add_job(dynamic_orchestrator_job, 'interval', hours=2)
    scheduler.add_job(passive_large_marketing_job, 'interval', days=3)
    scheduler.start()
    logging.info("🚀 Планувальник задач успішно підключено та запущено на фонові інтервали.")

async def start_bot():
    logging.info("🤖 Ініціалізація підключення до Telegram...")
    # Реєструємо наш миттєвий старт у диспетчері aiogram
    dp.startup.register(on_startup)
    await dp.start_polling(bot)
