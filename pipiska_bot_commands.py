from aiogram import types
import random
from datetime import datetime, timedelta

import config
from data_management import update_user_data, get_top_10_users, get_antitop_10_users, set_promo_used, get_user_data, \
    check_and_reset_promo,read_data


ADMIN_IDS=[1737504137, 987654321]


async def handle_top10(message: types.Message):
    if message.chat.type == types.ChatType.GROUP or message.chat.type == types.ChatType.SUPERGROUP:
        chat_id = message.chat.id
        top_users = get_top_10_users(chat_id)
        response = "Топ-10 Больших Валын:\n" + "\n".join(
            f"{index}. {user['username']} : {user['size']} см" for index, user in enumerate(top_users, 1))
        await message.reply(response)
    else:
        await message.reply("Эта команда доступна только в беседах.")


async def handle_antitop(message: types.Message):
    if message.chat.type == types.ChatType.GROUP or message.chat.type == types.ChatType.SUPERGROUP:
        chat_id = message.chat.id
        antitop_users = get_antitop_10_users(chat_id)
        response = "Топ-10 Маленьких Валын:\n" + "\n".join(
            f"{index}. {user['username']} : {user['size']} см" for index, user in
            enumerate(reversed(antitop_users), 1))
        await message.reply(response)
    else:
        await message.reply("Эта команда доступна только в беседах.")


async def handle_size_change(message: types.Message):
    if message.chat.type == types.ChatType.GROUP or message.chat.type == types.ChatType.SUPERGROUP:
        chat_id = message.chat.id  # Получаем chat_id текущего чата
        username = message.from_user.username
        delay = config.EXCLUSIVE_DELAY_WHITELIST.get(chat_id, 3600)
        # Проверка времени последнего обновления
        user_data = get_user_data(chat_id, username)
        if user_data and 'last_update' in user_data:
            last_update_time = datetime.fromisoformat(user_data['last_update'])
            current_time = datetime.now()
            time_difference = current_time - last_update_time
            if time_difference < timedelta(seconds=delay):
                hours, remainder = divmod((timedelta(seconds=delay) - time_difference).seconds, 3600)
                minutes = remainder // 60
                await message.reply(
                    f"Вы уже использовали эту функцию сегодня. Следующая попытка через {hours} часов {minutes} минут!\nhttps://t.me/c/1626228917/219140\nhttps://t.me/c/1626228917/219141\nhttps://t.me/c/1626228917/219146")
                return

        # Установка разного значения change для специального пользователя
        if username == 'asstassi':
            change = random.uniform(6, 10)
        else:
            change = random.randint(-5, 10)

        new_size, position = update_user_data(chat_id, username, change)  # Передаем chat_id, username и change

        if new_size is None:
            await message.reply("Вы уже использовали эту функцию сегодня. Следующая попытка через {hours} часов {minutes}!")
            return

        await message.reply(
            f"@{username}, твой показатель изменился на {change:.1f} см. Теперь он равен {new_size} см. Ты занимаешь {position} место в рейтинге. Следующая попытка через {delay//3600} час!\nhttps://t.me/c/1626228917/219140\nhttps://t.me/c/1626228917/219141\nhttps://t.me/c/1626228917/219146")
    else:
        await message.reply("Эта команда доступна только в беседах.")


promo_usage_count = 0
current_date = datetime.now().date()


async def handle_promo(message: types.Message):
    global promo_usage_count, current_date

    if message.chat.type == types.ChatType.GROUP or message.chat.type == types.ChatType.SUPERGROUP:
        chat_id = message.chat.id
        username = message.from_user.username
        check_and_reset_promo(chat_id, username)

        # Проверяем, начался ли новый день
        if datetime.now().date() != current_date:
            promo_usage_count = 0
            current_date = datetime.now().date()

        # Получаем данные пользователя
        user_data = get_user_data(chat_id, username)

        # Проверяем, использовал ли пользователь уже промокод сегодня
        if user_data and user_data.get('promo_used') == 'True':
            await message.reply("Вы уже использовали промокод. Дождитесь следующего!")
            return

        # Проверяем, не достигнуто ли ограничение на количество использований промокода за день
        if promo_usage_count >= 5:
            await message.reply("Превышено ограничение на количество использований промокода.")
            return

        # Применяем изменения для пользователя
        change = 30  # Значение изменения
        new_size, position = update_user_data(chat_id, username, change, True, use_promo=True)

        # Устанавливаем флаг использования промокода
        set_promo_used(chat_id, username, 'True', increase_count=True)

        # Увеличиваем счетчик использований промокода за день
        promo_usage_count += 1

        # Проверяем общее количество использований промокода в топ-10 пользователей
        total_promo_count = sum([int(user.get('promo_count', '0')) for user in get_top_10_users(chat_id) if user.get('promo_count', '0')])

        await message.reply(
            f"Промокод успешно использован! Твой показатель изменился на {change:.1f} см. Теперь он равен {new_size} см. Ты занимаешь {position} место в рейтинге. Общее количество использований промокода: {total_promo_count}")
    else:
        await message.reply("Эта команда доступна только в беседах.")


async def handle_reset_promo(message: types.Message):
    user_id = message.from_user.id

    if user_id in ADMIN_IDS:
        reset_promo()
        await message.reply("Промокоды были успешно сброшены.")
    else:
        await message.reply("У вас нет прав для выполнения этой команды.")

def reset_promo():
    global promo_usage_count, current_date
    promo_usage_count = 0
    current_date = datetime.now().date()
    reset_promo_flag_for_all_users()

def reset_promo_flag_for_all_users():
    users = read_data()  # Используйте функцию чтения данных, чтобы получить всех пользователей
    for user in users:
        set_promo_used(user['chat_id'], user['username'], 'False', reset_time=True)

def setup_handlers(dp):
    dp.message_handler(commands=['top'])(handle_top10)
    dp.message_handler(commands=['antitop'])(handle_antitop)
    dp.message_handler(commands=['pipiska'])(handle_size_change)
    #dp.message_handler(commands=['promo'])(handle_promo)
    dp.message_handler(commands=['reset_promo_usage'])(handle_reset_promo)