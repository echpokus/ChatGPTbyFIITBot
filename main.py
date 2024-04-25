import asyncio
from aiogram import Bot, Dispatcher, types
from config import TELEGRAM_TOKEN
from family_bot import handle_wedding, handle_divorce, handle_family
from gpt_chat_commands import setup_gpt_chat_handlers
from pipiska_bot_commands import setup_handlers
from aneki_bot import send_random_anek  # Добавлено


async def main():
    bot = Bot(token=TELEGRAM_TOKEN)
    dp = Dispatcher(bot)

    setup_gpt_chat_handlers(dp, bot)
    setup_handlers(dp)

    # Настройка обработчиков команд из family_bot.py
    dp.message_handler(commands=['wedding'])(handle_wedding)
    dp.message_handler(commands=['divorce'])(handle_divorce)
    dp.message_handler(commands=['family'])(handle_family)

    # Регистрация обработчика для команды /anek
    dp.message_handler(commands=['anek'])(send_random_anek)

    await dp.start_polling()


if __name__ == '__main__':
    asyncio.run(main())
