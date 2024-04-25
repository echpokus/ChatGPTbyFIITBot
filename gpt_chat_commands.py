import time
from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher.filters import Command, Text
import openai
import asyncio
import os
from gtts import gTTS
from tokens import OPENAI_API_KEY, TELEGRAM_TOKEN
from logging_utils import notify_admin_and_log

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from pipiska_bot_commands import handle_size_change, handle_top10, handle_antitop
from tokens import OPENAI_API_KEY, TELEGRAM_TOKEN
from logging_utils import notify_admin_and_log

# Инициализация OpenAI
openai.api_key = OPENAI_API_KEY

# Инициализация бота
bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher(bot)

message_count = 0
keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton("Вырастить пипиську", callback_data='pipiska'),
            KeyboardButton("Топ", callback_data='top'),
            KeyboardButton("Антитоп", callback_data='antitop')
        ],
        [
            KeyboardButton("Поддержать бота", callback_data='donate')
        ]
    ],
    resize_keyboard=True,
    one_time_keyboard=False
)


async def send_welcome(message: types.Message, bot):
    await message.reply(
        "Привет! Я GPT-3.5 бот.\nИспользуйте команду /m@ChatGPTbyFIITBot [сообщение] для взаимодействия в чатах.\nИспользуйте команду /m [сообщение] для взаимодействия в личных сообщениях.\nИспользуйте команду /wedding для создания новой семьи.\nИспользуйте команду /divorce для развода.\nИспользуйте команду /family для уточнения информации о всех парах.\nИспользуйте команду /anek для получения крутой шутки.\nНо сначала подпишитесь на меня в инстаграмм (echpokus) <3\nТакже добавляйте бота в свои чаты :>\n\n\nЕсли хотите поддержать бота:\nhttps://www.tinkoff.ru/cf/ANd16yXFVM7 ",
        reply_markup=keyboard)


async def handle_command(message: types.Message, bot):
    match message.text:
        case 'Поддержать бота':
            await handle_donate_command(message)
        case 'Топ':
            await handle_top10(message)
        case 'Антитоп':
            await handle_antitop(message)
        case 'Вырастить пипиську':
            await handle_size_change(message)
        case _:  # Default case
            pass


async def handle_donate_command(message: types.Message):
    await message.reply(
        "Если хотите помочь переходу на ГПТ 4 и качественный хостинг\n https://www.tinkoff.ru/cf/ANd16yXFVM7 .")


async def send_help(message: types.Message, bot):
    await message.reply(
        "/m@ChatGPTbyFIITBot [сообщение] - получить ответ от GPT-3.5 в чате. \n/m [сообщение] - получить ответ от GPT-3.5 в личных сообщениях.\n/pipiska - Увеличение размера валыны.\n/top - Топ 10 больших валын.\n/antitop - Топ 10 маленьких валын.\n/wedding @муж @жена - создание новой семьи.\n/divorce @муж @жена - развод пары.\n/family - уточнение информации о всех парах.\n/anek - крутой анекдот.\n/help - список команд.\nТакже добавляйте бота в свои чаты :>\n\n\nЕсли хотите поддержать бота:\nhttps://www.tinkoff.ru/cf/ANd16yXFVM7")


async def handle_message(message: types.Message, bot):
    # Get the username of the message sender
    global message_count
    username = message.from_user.username
    user_id = message.from_user.id

    # List of blocked usernames and user IDs
    blocked_usernames = ['jakobswft']  # Make sure the username is correctly cased
    blocked_user_ids = [147989766]  # Example user ID; replace with actual ID if needed

    # Check if the user is blocked by username or ID
    if (username and username.lower() in (name.lower() for name in blocked_usernames)) or user_id in blocked_user_ids:
        await message.reply("Вы заблокированы и не можете использовать этого бота.")
        return

    user_input = message.get_args() if message.is_command() else message.text
    if not user_input and not message.is_command():
        await message.reply("Пожалуйста, отправьте мне текст для ответа.")
        return

    try:
        # Отправка запроса к OpenAI
        gpt_response = await asyncio.to_thread(
            openai.ChatCompletion.create,
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": user_input}]
        )
        response_text = gpt_response.choices[0].message.content
        await message.reply(response_text)

        # Преобразование текста в голосовое сообщение
        # tts = gTTS(response_text, lang='ru')
        # tts.save("response_raw.mp3")

        # with open("response_raw.mp3", "rb") as audio:
        #     await bot.send_voice(chat_id=message.chat.id, voice=audio)

        message_count += 1
        if message_count >= 7:
            message_count = 0
            await message.reply(
                "Если хотите помочь переходу на ГПТ 4 и качественный хостинг\n https://www.tinkoff.ru/cf/ANd16yXFVM7 .")



    except Exception as e:
        await message.reply("Ошибка. Обратитесь к администратору бота - @vsemenov")
        await notify_admin_and_log(bot, message, error=e)
    # finally:
    #     if os.path.exists("response_raw.mp3"):
    #         if os.path.exists("response.mp3"):
    #             time.sleep(1)
    #             os.remove("response.mp3")


def setup_gpt_chat_handlers(dp, bot):
    dp.message_handler(commands=['start'])(lambda message: send_welcome(message, bot))
    dp.message_handler(commands=['help'])(lambda message: send_help(message, bot))
    dp.message_handler(Command('m'))(lambda message: handle_message(message, bot))
    # Обработчик для всех текстовых сообщений в личных чатах
    dp.message_handler(content_types=['text'], chat_type=types.ChatType.PRIVATE)(
        lambda message: handle_message(message, bot))
    dp.message_handler(content_types=['text'], chat_type=types.ChatType.GROUP or types.ChatType.SUPERGROUP)(
        lambda message: handle_command(message, bot))


setup_gpt_chat_handlers(dp, bot)

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
