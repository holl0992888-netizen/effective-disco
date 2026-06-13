import asyncio
import logging
from dotenv import load_dotenv
from BotCore.core import start_bot

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - [%(levelname)s] - %(name)s - %(message)s"
)

async def main():
    load_dotenv()
    logging.info("🚀 Запуск безкоштовної автономної системи на Railway...")
    await start_bot()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("🛑 Систему зупинено адміністратором.")
