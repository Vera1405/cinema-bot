from telegram import ReplyKeyboardMarkup
from random import choice


def throw_a_cube(num, count=1):
    sequence = []
    result = []
    for _ in range(1, num + 1):
        sequence.append(_)
    for i in range(count):
        result.append(str(choice(sequence)))
    return result


def dice(update, context):
    reply_keyboard = [['🎲 Кинуть один шестигранный кубик',
                       '🎲 🎲Кинуть 2 шестигранных кубика одновременно'],
                      ['🎱 Кинуть 20-гранный кубик', '⏪ Вернуться назад']]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)

    update.message.reply_text('Как кинуть кубик?',
                              reply_markup=markup)
