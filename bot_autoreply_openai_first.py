#отвечает используя chatgpt api? преднастроенного ассистента - только на первое сообщение

from telethon import TelegramClient, events
from openai import OpenAI
import os
import time

# Установите API-ключ OpenAI
# Установите API-ключ OpenAI
open_ai_token = 'sk-proj-iWCfXQRw'
ASSISTANT_ID = 'asst_6i'


# Создаем клиент OpenAI
openai_client = OpenAI(api_key=open_ai_token)

# Данные для подключения к Telegram
api_id = 295 # замените на ваш API_ID, например: 123456
api_hash = '1dbbfa972'

# Путь к лог-файлу
LOG_FILE = 'message_log.txt'

# Создаем клиент Telegram
telegram_client = TelegramClient('7991_session_name', api_id, api_hash)

# Проверяем, существует ли лог-файл, если нет — создаем
if not os.path.exists(LOG_FILE):
    open(LOG_FILE, 'w').close()

@telegram_client.on(events.NewMessage)
async def handle_new_message(event):
    # Проверяем, что сообщение входящее и личное
    if event.is_private and not event.out:
        sender_id = str(event.sender_id)  # Преобразуем в строку для сравнения
        # Читаем лог-файл и получаем список ID пользователей
        with open(LOG_FILE, 'r') as f:
            logged_users = f.read().splitlines()

        # Если ID отправителя нет в лог-файле, считаем сообщение первым
        if sender_id not in logged_users:
            user_message = event.message.message

            # Отправляем сообщение ассистенту OpenAI
            try:
                # Создаем новый тред
                thread = openai_client.beta.threads.create(
                    messages=[
                        {
                            "role": "user",
                            "content": user_message,
                        }
                    ]
                )
                # Запускаем тред с указанным ассистентом
                run = openai_client.beta.threads.runs.create(thread_id=thread.id, assistant_id=ASSISTANT_ID)

                # Ожидаем завершения обработки
                while run.status != "completed":
                    time.sleep(1)
                    run = openai_client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)

                # Получаем сообщения из треда
                message_response = openai_client.beta.threads.messages.list(thread_id=thread.id)
                messages = message_response.data

                # Ищем последнее сообщение от ассистента
                assistant_reply = None
                for message in reversed(messages):
                    if message.role == 'assistant':
                        assistant_reply = message.content[0].text.value
                        break

                if assistant_reply is None:
                    assistant_reply = "Не удалось получить ответ от ассистента."

            except Exception as e:
                assistant_reply = "Произошла ошибка при обработке вашего сообщения."
                print(f"Ошибка при обращении к OpenAI API: {e}")

            # Отправляем ответ ассистента обратно собеседнику
            await event.respond(assistant_reply)

            # Добавляем ID отправителя в лог-файл
            with open(LOG_FILE, 'a') as f:
                f.write(f"{sender_id}\n")

# Запускаем клиента Telegram
telegram_client.start()
telegram_client.run_until_disconnected()
