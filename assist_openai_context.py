#общается с собеседником на основе chatgpt, но с учетом предидущего контекста (имеет память. отправляется последние 10 сообщений).
from telethon import TelegramClient, events
from openai import OpenAI
import os
import time
import re

# Установите API-ключ OpenAI
open_ai_token = 'sk-proj-iWCfXQ'
ASSISTANT_ID = 'asst_6if'
#ASSISTANT_ID = 'asst_uLe8O'

# Создаем клиент OpenAI
openai_client = OpenAI(api_key=open_ai_token)

# Данные для подключения к Telegram
api_id = 295 # замените на ваш API_ID, например: 123456
api_hash = '1dbbfa971e44f'  # замените на ваш API_HASH, например: 'abcdef1234567890abcdef1234567890'

# Папка для хранения лог-файлов
LOG_FOLDER = 'dialog_logs'

# Создаем папку для логов, если она не существует
if not os.path.exists(LOG_FOLDER):
    os.makedirs(LOG_FOLDER)

# Создаем клиент Telegram
telegram_client = TelegramClient('79912015867_session_name', api_id, api_hash)

@telegram_client.on(events.NewMessage)
async def handle_new_message(event):
    # Проверяем, что сообщение входящее и личное
    if event.is_private and not event.out:
        user_message = event.message.message.strip()
        sender = await event.get_sender()
        sender_id = sender.id  # Идентификатор пользователя
        sender_name = sender.first_name if sender.first_name else "Unknown"

        # Имя лог-файла для этого собеседника
        log_filename = f"{sender_id}.txt"
        log_filepath = os.path.join(LOG_FOLDER, log_filename)

        # Сохраняем новое сообщение от собеседника в лог-файл
        with open(log_filepath, 'a', encoding='utf-8') as log_file:
            log_file.write(f"собеседник: {user_message}\n")

        # Читаем весь лог-файл и разбиваем на сообщения
        messages = []
        if os.path.exists(log_filepath):
            with open(log_filepath, 'r', encoding='utf-8') as log_file:
                content = log_file.read()

                # Используем регулярное выражение для разделения сообщений
                pattern = r'(?:^|\n)(я|собеседник):'
                splits = re.split(pattern, content)
                # re.split возвращает список, где четные элементы — метки, нечетные — сообщения

                # Объединяем метки и сообщения
                temp_messages = []
                for i in range(1, len(splits), 2):
                    role = splits[i].strip()
                    message = splits[i+1].strip()
                    full_message = f"{role}: {message}"
                    temp_messages.append(full_message)

                messages = temp_messages

        # Берем последние 10 сообщений
        last_messages = messages[-10:]

        # Подготавливаем контекст для ассистента
        context_lines = []
        for msg in last_messages:
            # Заменяем "я:" на "ты:", "собеседник:" на "я:"
            msg_replaced = msg.replace("я:", "ты:").replace("собеседник:", "я:")
            context_lines.append(msg_replaced)

        # Добавляем новое сообщение
        context = "\n".join(context_lines)
        prompt = f"Наши предыдущие сообщения:\n\n{context}\n\nМое новое сообщение: {user_message}"

        # Отправляем сообщение ассистенту OpenAI
        try:
            # Создаем новый тред с контекстом
            thread = openai_client.beta.threads.create(
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
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
            response_messages = message_response.data

            # Ищем последнее сообщение от ассистента
            assistant_reply = None
            for message in reversed(response_messages):
                if message.role == 'assistant':
                    assistant_reply = message.content[0].text.value.strip()
                    break

            if assistant_reply is None:
                assistant_reply = "Не удалось получить ответ от ассистента."

        except Exception as e:
            assistant_reply = "Произошла ошибка при обработке вашего сообщения."
            print(f"Ошибка при обращении к OpenAI API: {e}")

        # Отправляем ответ ассистента обратно собеседнику
        await event.respond(assistant_reply)

        # Сохраняем ответ ассистента в лог-файл
        with open(log_filepath, 'a', encoding='utf-8') as log_file:
            log_file.write(f"я: {assistant_reply}\n")

# Запускаем клиента Telegram
telegram_client.start()
telegram_client.run_until_disconnected()
