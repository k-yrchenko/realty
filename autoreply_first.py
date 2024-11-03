#простой автоответчик на первое сообщение
import asyncio
from telethon import TelegramClient, events
import os
import logging

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


api_id = 29  # замените на ваш API_ID, например: 123456
api_hash = '1dbbfa971'  # замените на ваш API_HASH, например: 'abcdef1234567890abcdef1234567890'
#PHONE_NUMBER = '79912015867'


# Имя сессии изменено на '79912015867_session_name'
client = TelegramClient('799_session_name', api_id, api_hash)

# Путь к файлу с обработанными пользователями
processed_users_file = 'processed_users.txt'

# Загружаем обработанных пользователей при старте
def load_processed_users():
    if not os.path.exists(processed_users_file):
        return set()
    with open(processed_users_file, 'r') as f:
        return set(line.strip() for line in f if line.strip().isdigit())

# Сохраняем обработанного пользователя в файл и в множество
def save_processed_user(user_id, processed_users):
    with open(processed_users_file, 'a') as f:
        f.write(f"{user_id}\n")
    processed_users.add(str(user_id))

# Обработчик новых сообщений
class AutoResponder:
    def __init__(self):
        self.processed_users = load_processed_users()

    async def handler(self, event):
        sender = await event.get_sender()
        if sender is None:
            logger.warning("Не удалось получить отправителя сообщения.")
            return
        user_id = sender.id

        # Проверяем, был ли пользователь уже обработан
        if str(user_id) not in self.processed_users:
            try:
                # Отправляем ответ
                await event.reply("привет. квартирка сдается. если вы ранее не кстати это автоответчик.")
                # Сохраняем пользователя как обработанного
                save_processed_user(user_id, self.processed_users)
                logger.info(f"Отправлен автоответ пользователю {user_id}")
            except Exception as e:
                logger.error(f"Не удалось отправить сообщение пользователю {user_id}: {e}")

async def main():
    responder = AutoResponder()
    client.add_event_handler(responder.handler, events.NewMessage(incoming=True))
    await client.start()
    logger.info("Бот запущен и работает...")
    await client.run_until_disconnected()

if __name__ == '__main__':
    asyncio.run(main())

