#отвечает используя chatgpt api? преднастроенного ассистента - на все сообщения, а не только на первое
from telethon import TelegramClient, events
from openai import OpenAI
import os
import time

# Установите API-ключ OpenAI
open_ai_token = 'sk-proj-iWCf'
#ASSISTANT_ID = 'asst_6i'
ASSISTANT_ID = 'asst_u'

# Создаем клиент OpenAI
openai_client = OpenAI(api_key=open_ai_token)

# Данные для подключения к Telegram
api_id = 295  # замените на ваш API_ID, например: 123456
api_hash = '1dbbfa971e44'

# Создаем клиент Telegram
telegram_client = TelegramClient('79912015867_session_name', api_id, api_hash)

@telegram_client.on(events.NewMessage)
async def handle_new_message(event):
    # Проверяем, что сообщение входящее и личное
    if event.is_private and not event.out:
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

# Запускаем клиента Telegram
telegram_client.start()
telegram_client.run_until_disconnected()
