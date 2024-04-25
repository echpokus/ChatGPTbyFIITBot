import logging
import re
import csv
from tokens import ADMIN_USER_ID

LOGS_TXT_FILE = 'chat_logs.txt'
LOGS_CSV_FILE = 'logs.csv'

# Настройка логгирования
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

def read_chat_logs():
    """ Читает логи из файла chat_logs.txt и возвращает список уникальных записей. """
    logs = {}
    with open(LOGS_TXT_FILE, 'r', encoding='utf-8') as file:
        for line in file:
            match = re.search(r"Пользователь: (\d+), Имя: @(\w+).*\n", line)
            if match:
                user_id = match.group(1)
                username = match.group(2)
                logs[user_id] = {'user_id': user_id, 'username': username}
    return list(logs.values())

def update_logs_csv(logs):
    """ Обновляет или создает файл logs.csv на основе прочитанных логов. """
    with open(LOGS_CSV_FILE, 'w', newline='', encoding='utf-8') as file:
        fieldnames = ['user_id', 'username']
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for log in logs:
            writer.writerow(log)

async def notify_admin_and_log(bot, message, response=None, error=None):
    """ Функция для уведомления администратора и логирования в файл """
    log_message = f"Сообщение от пользователя: {message.from_user.username} ({message.from_user.id})\n\n"
    log_message += f"Текст сообщения: {message.text}\n\n"
    if response:
        # Если есть ответ, не записывать его в личный чат администратора
        pass
    if error:
        log_message += f"Ошибка: {error}\n"

    try:
        with open(LOGS_TXT_FILE, "a", encoding="utf-8") as log_file:
            log_file.write(log_message + "\n")
    except Exception as e:
        logger.error(f"Ошибка при записи в файл логов: {e}")