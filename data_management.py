import os
import csv
from datetime import datetime, timedelta

DATA_FILE = '../../../../Downloads/Telegram Desktop/users_data.csv'
DATA_DIRECTORY = 'chat_data'


def get_data_filename(chat_id):
    data_file = os.path.join(DATA_DIRECTORY, f"{chat_id}_users_data.csv")
    os.makedirs(os.path.dirname(data_file), exist_ok=True)
    return data_file


def read_data(chat_id):
    data_file = get_data_filename(chat_id)
    try:
        with open(data_file, 'r', newline='', encoding='utf-8') as file:
            return list(csv.DictReader(file))
    except FileNotFoundError:
        return []


def write_data(chat_id, users):
    data_file = get_data_filename(chat_id)
    with open(data_file, 'w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=['username', 'size', 'last_update', 'promo_used', 'promo_count',
                                                  'last_promo_use'])
        writer.writeheader()
        writer.writerows(users)


def get_user_data(chat_id, username):
    users = read_data(chat_id)
    return next((u for u in users if u['username'] == username), None)


def set_promo_used(chat_id, username, used, increase_count=False, reset_time=False, use_promo=False):
    users = read_data(chat_id)
    user = next((u for u in users if u['username'] == username), None)

    if user:
        if reset_time or (user.get('last_promo_use') and (
                user['last_promo_use'] == '1' or
                (datetime.now() - datetime.fromisoformat(user['last_promo_use']) > timedelta(minutes=30)))):
            user['promo_used'] = 'False'
            user['last_promo_use'] = datetime.now().isoformat()
        else:
            if not user.get('promo_used') or use_promo:
                user['promo_used'] = used
        if increase_count:
            # Убедитесь, что promo_count не является пустой строкой
            current_count = user.get('promo_count', '0')
            current_count = 0 if current_count == '' else int(current_count)
            user['promo_count'] = str(current_count + 1)
    else:
        # Создать новую запись, если пользователя нет в базе данных
        new_user = {
            'username': username,
            'size': '0',  # Установите значение по умолчанию для size, если нужно
            'last_update': datetime.now().isoformat(),
            'promo_used': used if use_promo else 'False',  # Изменено здесь
            'promo_count': '0',
        }
        if reset_time:
            new_user['last_promo_use'] = datetime.now().isoformat()
        else:
            if not new_user.get('promo_used') or use_promo:
                new_user['promo_used'] = used
        users.append(new_user)

    write_data(chat_id, users)


def update_user_data(chat_id, username, change, ignore_time_check=False, use_promo=False):
    users = read_data(chat_id)
    user = next((u for u in users if u['username'] == username), None)
    now = datetime.now()

    if user:
        if not ignore_time_check:
            if use_promo:
                last_use = user.get('last_promo_use')
            else:
                last_use = user.get('last_update')

            if last_use and now - datetime.fromisoformat(last_use) < timedelta(hours=1):
                return None, None

        user['size'] = str(float(user['size']) + change)
    else:
        user = {'username': username, 'size': str(change), 'last_update': now.isoformat(), 'promo_used': False,
                'promo_count': '0', 'last_promo_use': None}
        users.append(user)

    if use_promo:
        user['last_promo_use'] = now.isoformat()
    else:
        user['last_update'] = now.isoformat()

    users.sort(key=lambda x: float(x['size']), reverse=True)
    position = users.index(user) + 1
    write_data(chat_id, users)
    return user['size'], position


def check_and_reset_promo(chat_id, username):
    user_data = get_user_data(chat_id, username)
    if user_data:
        last_promo_use = user_data.get('last_promo_use')
        if last_promo_use and datetime.now() - datetime.fromisoformat(last_promo_use) > timedelta(days=1):
            set_promo_used(chat_id, username, 'False', reset_time=True, use_promo=True)



def get_top_10_users(chat_id):
    users = read_data(chat_id)
    users.sort(key=lambda x: float(x['size']), reverse=True)
    return users[:10]


def get_antitop_10_users(chat_id):
    users = read_data(chat_id)
    return users[-10:]