import os
import logging

class MarketingHub:
    def __init__(self):
        self.channel_id = os.getenv("CHANNEL_ID")
        self.username = os.getenv("CHANNEL_USERNAME", "my_channel")

    async def check_channel_subscribers(self, bot) -> int:
        """
        Аналіз кількості аудиторії.
        """
        try:
            count = await bot.get_chat_member_count(chat_id=self.channel_id)
            return count
        except Exception as e:
            logging.error(f"Помилка підрахунку підписників: {e}")
            return 0

    async def execute_smart_vp(self, bot, current_subs: int):
        """
        Автоматична підготовка та розсилка пропозицій взаємного піару.
        """
        logging.info(f"🤝 Маркетинг: Запуск пошуку ВП для каналу з {current_subs} підписниками...")
        
        partner_text = f"📢 Рекомендація від адміна: Завітайте на канал наших партнерів із закритими розпродажами!"
        try:
            await bot.send_message(chat_id=self.channel_id, text=partner_text)
            logging.info("✅ Пост взаємного піару успішно розміщено.")
        except Exception as e:
            logging.error(f"Помилка публікації ВП: {e}")

    def generate_viral_invite(self) -> str:
        """
        Вірусний пост для припливу нових користувачів.
        """
        return (
            f"🎁 **АКЦІЯ: Приведи друга — отримай секретну знижку!** 🎁\n\n"
            f"Поділися цим постом із 3 друзями, які люблять економити на покупках. "
            f"Щойно вони підпишуться, наш бот автоматично відкриє для тебе доступ до секретних промокодів!\n\n"
            f"🔗 Твоє унікальне запрошення: https://t.me{self.username}"
        )
