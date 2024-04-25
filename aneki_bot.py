import logging
from aiogram import Bot, Dispatcher, executor, types
import random
import csv
from tokens import TELEGRAM_TOKEN  # Убедитесь, что у вас есть файл tokens.py с переменной TELEGRAM_TOKEN

# Конфигурация логирования
logging.basicConfig(level=logging.INFO)

# Инициализация бота
bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher(bot)

# Обработчик команды /anek
@dp.message_handler(commands=['anek'])
async def send_random_anek(message: types.Message):
    try:
        # Читаем файл и выбираем случайное сообщение
        with open('aneki.csv', 'r', encoding='utf-8') as file:
            reader = list(csv.reader(file))
            selected_row = random.choice(reader)

        # Отправляем сообщение
        await message.reply(selected_row[0])

    except Exception as e:
        await message.reply('Произошла ошибка!')

# Запуск бота
if __name__ == '__main__':
    from aiogram import executor
    executor.start_polling(dp, skip_updates=True)
