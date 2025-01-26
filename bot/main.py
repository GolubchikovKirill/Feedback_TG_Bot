import logging
import sys
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from config import BOT_TOKEN
from handlers.messages import message_handler
from handlers.buttons import button_handler
import subprocess
import asyncio
import os


class FeedbackBot:
    """Основной класс бота для сбора обратной связи"""
    
    def __init__(self, token: str):
        self.bot = Bot(token=token)
        self.dp = Dispatcher(storage=MemoryStorage())
        self._setup_logging()
        self._setup_routers()

    def _setup_logging(self):
        """Настройка логирования"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)

    def _setup_routers(self):
        """Подключение роутеров обработчиков"""
        self.dp.include_router(message_handler.router)
        self.dp.include_router(button_handler.router)

    def start_admin_panel(self):
        """Запуск админ-панели как отдельного процесса"""
        try:
            admin_path = os.path.join(os.path.dirname(__file__), "admin.py")
            subprocess.Popen([sys.executable, admin_path])  # Используем текущую версию Python
            self.logger.info("Admin panel started successfully")
        except Exception as e:
            self.logger.error(f"Error starting admin panel: {e}")

    async def start(self):
        """Запуск бота"""
        try:
            self.logger.info("Starting feedback bot...")
            await self.bot.delete_webhook()  # Удаляем вебхук перед start_polling
            self.start_admin_panel()
            await self.dp.start_polling(self.bot)
        except Exception as e:
            self.logger.error(f"Error starting bot: {e}")
        finally:
            self.logger.info("Bot stopped")

def main():
    """Точка входа в приложение"""
    bot = FeedbackBot(BOT_TOKEN)
    asyncio.run(bot.start())

if __name__ == "__main__":
    main()
