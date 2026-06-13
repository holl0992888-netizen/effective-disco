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
    channel_id = os.getenv("CHANNEL_ID")
    subs_count = await marketing_hub.check_channel_subscribers(bot)
    
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

    if subs_count < 500:
        logging.info("⚠️ АКТИВОВАНО РЕЖИМ СТАРТОВОГО РОЗВИТКУ!")
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

# Виправлено логіку черговості запуску потоків
async def on_startup():
    scheduler.add_job(dynamic_orchestrator_job, 'interval', hours=2)
    scheduler.add_job(passive_large_marketing_job, 'interval', days=3)
    scheduler.start()
    logging.info("🚀 Планувальник APScheduler успішно запущено після авторизації бота.")

async def start_bot():
    logging.info("🤖 Ініціалізація підключення до Telegram...")
    # Реєструємо функцію запуску розкладу ПІСЛЯ старту лонг-полінгу
    dp.startup.register(on_startup)
    await dp.start_polling(bot)
