from data_family import read_family_data, write_family_data
from datetime import datetime
from aiogram import types, Bot, Dispatcher
import asyncio

# CSV-файл для хранения данных о семьях
FAMILIES_DATA_FILE = 'family.csv'

# Функции для работы с данными о семьях
def create_family(husband_username, wife_username, wedding_date):
    families = read_family_data()
    families.append({'husband': husband_username, 'wife': wife_username, 'wedding_date': wedding_date})
    write_family_data(families)

def divorce_family(husband_username, wife_username):
    families = read_family_data()
    families = [family for family in families if family['husband'] != husband_username or family['wife'] != wife_username]
    write_family_data(families)

def get_all_families():
    families = read_family_data()
    return families

def congratulate_families_on_anniversary():
    today = datetime.now()
    families = read_family_data()
    for family in families:
        wedding_date = datetime.strptime(family['wedding_date'], '%d-%m-%Y')
        if today.day == wedding_date.day and today.month == wedding_date.month:
            husband_username = family['husband']
            wife_username = family['wife']
            message = f"Дорогие @{husband_username} и @{wife_username}! Поздравляем вас с годовщиной свадьбы! 🎉"
            bot.send_message(message)

# Обработчики команд
async def handle_wedding(message: types.Message):
    # Обработка команды для создания семьи
    if len(message.text.split()) != 3:
        await message.reply("Неверный формат команды. Используйте: /wedding @муж @жена")
        return

    husband_username = message.text.split()[1]
    wife_username = message.text.split()[2]

    # Проверяем, что муж и жена не являются одним и тем же пользователем
    if husband_username == wife_username:
        await message.reply("Вы не можете жениться сами на себе.")
        return

    # Проверяем, что пользователь ещё не состоит в семье
    families = get_all_families()
    for family in families:
        if husband_username in [family['husband'], family['wife']] or wife_username in [family['husband'], family['wife']]:
            await message.reply("Вы уже состоите в семье и не можете жениться повторно.")
            return

    # Устанавливаем дату создания семьи как день отправки сообщения
    wedding_date = message.date.strftime('%d-%m-%Y')

    create_family(husband_username, wife_username, wedding_date)
    await message.reply(f"Семья создана между {husband_username} и {wife_username} 🎉🎉🎉")


async def handle_divorce(message: types.Message):
    # Обработка команды для развода семьи
    if len(message.text.split()) != 3:
        await message.reply("Неверный формат команды. Используйте: /divorce @муж @жена")
        return
    husband_username = message.text.split()[1]
    wife_username = message.text.split()[2]
    divorce_family(husband_username, wife_username)
    await message.reply(f"Семья между {husband_username} и {wife_username} разрушена💔💔💔")

async def handle_family(message: types.Message):
    # Обработка команды для вывода списка семей
    families = get_all_families()
    if not families:
        await message.reply("В данный момент нет семей.")
    else:
        family_list = "\n".join([f"{family['husband']} - {family['wife']} вместе c {family['wedding_date']}" for family in families])
        await message.reply(f"Список всех семей:\n{family_list}")

# Начало бота
if __name__ == '__main__':
    from config import TELEGRAM_TOKEN

    # Создание бота и диспетчера
    bot = Bot(token=TELEGRAM_TOKEN)
    dp = Dispatcher(bot)

    # Настройка обработчиков команд
    dp.message_handler(commands=['wedding'])(handle_wedding)
    dp.message_handler(commands=['divorce'])(handle_divorce)
    dp.message_handler(commands=['family'])(handle_family)

    # Запуск бота
    asyncio.run(dp.start_polling())