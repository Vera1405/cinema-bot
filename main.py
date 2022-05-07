from telegram.ext import *
from telegram import *
from other.weather import weather
from other.comments import comments
from maps.closest_cinema import closest_cinema
from games.dice import throw_a_cube, dice
import argparse
import requests

parser = argparse.ArgumentParser()

try:
    parser.add_argument("token", nargs="*")
    args = parser.parse_args()
    updater_ = Updater(args.token[0])
except Exception:
    try:
        f = open("token.txt", encoding="utf8")
        updater_ = Updater(f.readlines()[-1])
    except Exception:
        print('Введите правильный токен')

try:
    p = open("pass.txt", encoding="utf8")
    admin_pass = p.readlines()[0]
except Exception:
    admin_pass = 'Arev141105'

user_name = ''
user_city = ''
user_address = ''
user_comment = ''
country = ''
is_admin = True

keyboard_main = [['Узнать погоду', 'Написать отзыв', 'Ввести новый адрес'],
                 ['Найти ближайший Синема Парк'],
                 ['Игры']]
keyboard_games = [['Кинуть кубик'],
                  ['Основные функции']]
keyboard_admin = [['Перезапустить бота']]
keyboard = keyboard_main


def main():
    global updater_
    dp = updater_.dispatcher
    conv_handler = ConversationHandler(
        # Точка входа в диалог.
        # В данном случае — команда /start. Она задаёт первый вопрос.
        entry_points=[CommandHandler('start', start)],

        # Состояние внутри диалога.
        states={
            1: [MessageHandler(Filters.text, get_city)],
            2: [MessageHandler(Filters.text, get_address)],
            3: [MessageHandler(Filters.text, second_start)],
            4: [MessageHandler(Filters.text, get_comments)],
            5: [MessageHandler(Filters.text, text_commands)],
        },

        fallbacks=[CommandHandler('stop', stop)]
    )
    dp.add_handler(conv_handler)


def start(update, context):
    global user_city
    global is_admin
    update.message.reply_text(
        'Введите ваш город и адрес, '
        'чтобы разблокировать весь функционал бота')
    update.message.reply_text('Введите город',
                              reply_markup=ReplyKeyboardRemove())
    return 1


def get_city(update, context):
    global user_city
    user_city = update.message.text
    update.message.reply_text('Введите адрес')
    return 2


def get_address(update, context):
    global user_address
    user_address = update.message.text
    reply_keyboard = [['Да', 'Нет']]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    update.message.reply_text(f'Ваш город: {user_city}')
    update.message.reply_text(f'Ваш адрес: {user_address}')
    update.message.reply_text('Вы правильно ввели данные?',
                              reply_markup=markup)
    return 3


def second_start(update, context):
    global user_city
    if update.message.text == 'Нет':
        update.message.reply_text('Введите город')
        return 1
    else:
        markup = ReplyKeyboardMarkup(keyboard)
        update.message.reply_text('Выберите действие',
                                  reply_markup=markup)
    return 5


def get_weather(update, context):
    global user_city
    if weather(user_city)["conditions"] is not None:
        update.message.reply_text(
            f'В городе {user_city} {weather(user_city)["conditions"]}')
        update.message.reply_text(
            f'Температура: {weather(user_city)["temp"]}C, самое время сходить в кино')
    else:
        update.message.reply_text(
            'Проверьте написание города и повторите попытку')


def get_closest_cinema(update, context):
    global user_city
    global user_address
    try:
        file_name = closest_cinema(user_city, user_address)[0]
        pharmacy_name = closest_cinema(user_city, user_address)[1]
        distance_to_pharmacy = closest_cinema(user_city, user_address)[2]
        pharmacy_address = closest_cinema(user_city, user_address)[3]
        pharmacy_time_of_works = closest_cinema(user_city, user_address)[4]
        update.message.reply_photo(photo=open(f'img/{file_name}', 'rb'))
        update.message.reply_text(
            f'{pharmacy_name} {pharmacy_time_of_works}')
        update.message.reply_text(
            f'Расстояние до {pharmacy_address}: {distance_to_pharmacy}м')
    except Exception as e:
        print(e)
        update.message.reply_text(
            f'Рядом с вами нет Синема Парка')


def get_comments(update, context):
    global user_comment
    global user_name
    user_name = update.message.from_user.username
    user_comment = update.message.text
    return 5


def text_commands(update, context):
    global user_comment
    global keyboard
    global current_city
    global game_is_played
    global is_admin
    global try_counter

    # Возвращение в начало
    if update.message.text == '/start':
        update.message.reply_text(
            'Введите ваш город и адрес, что'
            'бы разблокировать весь функционал бота')
        update.message.reply_text('Введите город')
        return 1

    # Ввод нового адреса
    if update.message.text == 'Ввести новый адрес':
        update.message.reply_text('Введите город')
        return 1

    # Ввод отзыва
    if update.message.text == 'Написать отзыв':
        reply_keyboard = [['Подтвердить']]
        markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
        update.message.reply_text(
            f'Сюда вы можете написать ваш отзыв', reply_markup=markup)
        return 4

    # Подтверждение отзыва
    if update.message.text == 'Подтвердить':
        print("user_comment =", user_comment)
        markup = ReplyKeyboardMarkup(keyboard)
        if user_comment != '':
            update.message.reply_text('Ваш отзыв успешно записан!',
                                      reply_markup=markup)
            comments(user_comment, user_name)
            user_comment = ''
        else:
            update.message.reply_text('Ваш отзыв пуст',
                                      reply_markup=markup)


    # Обрабтока команды вывода погоды
    if update.message.text == 'Узнать погоду':
        get_weather(update, context)

    # Обрабтока команды вывода ближайшего
    if update.message.text == 'Найти ближайший Синема Парк':
        get_closest_cinema(update, context)

    # Обрабтока команды на смены клавиатуры на игровую
    if update.message.text == 'Игры':
        keyboard = keyboard_games
        markup = ReplyKeyboardMarkup(keyboard)
        update.message.reply_text(
            f'Переключаю на клавиатуру "{update.message.text}"',
            reply_markup=markup)

    # Обрабтока команды на смены клавиатуры на основную
    if update.message.text == 'Основные функции':
        keyboard = keyboard_main
        markup = ReplyKeyboardMarkup(keyboard)
        update.message.reply_text(
            f'Переключаю на клавиатуру "{update.message.text}"',
            reply_markup=markup)

    # Возвращение в меню игр
    if update.message.text == '⏪ Вернуться назад':
        markup = ReplyKeyboardMarkup(keyboard)
        update.message.reply_text('Возвращаемся назад', reply_markup=markup)

    # Кидаемй кубик
    if update.message.text == 'Кинуть кубик':
        dice(update, context)

    # Кидаем один шестигранный кубик
    if update.message.text == '🎲 Кинуть один шестигранный кубик':
        update.message.reply_text(' '.join(throw_a_cube(6)))

    # Кидаем 2 шестигранных кубика одновременно
    if update.message.text == '🎲 🎲Кинуть 2 шестигранных кубика одновременно':
        update.message.reply_text(' '.join(throw_a_cube(6, 2)))

    # Кидаем 20-гранный кубик
    if update.message.text == '🎱 Кинуть 20-гранный кубик':
        update.message.reply_text(' '.join(throw_a_cube(20)))

    # Вход в админ панель
    if update.message.text == admin_pass:
        is_admin = True
        markup = ReplyKeyboardMarkup(keyboard_admin)
        update.message.reply_text(
            'Вы получили доступ к админ панели', reply_markup=markup)

    # Обработка команды с админ клавиатуры на перезапуск бота
    if update.message.text == 'Перезапустить бота':
        markup = ReplyKeyboardMarkup(keyboard)
        if is_admin is True:
            update.message.reply_text('Перезапускаю...')
            update.message.reply_text(
                'Введите ваш город и адрес, что'
                'бы разблокировать весь функционал бота',
                reply_markup=ReplyKeyboardRemove())
            update.message.reply_text('Введите город')
            return 1
        else:
            update.message.reply_text('Кажется вы не админ',
                                      reply_markup=markup)


def stop(update, context):
    update.message.reply_text(
        "До свидания")
    return ConversationHandler.END  # Константа, означающая конец диалога.


if __name__ == '__main__':
    main()
    try:
        updater_.start_polling()
        updater_.idle()
    except Exception:
        pass
