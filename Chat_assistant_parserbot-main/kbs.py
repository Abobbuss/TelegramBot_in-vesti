from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton


def main_menu():
    keyboard = InlineKeyboardMarkup(row_width=1)
    buttons = [
        InlineKeyboardButton("Мероприятия", callback_data='events'),
        InlineKeyboardButton("Предложения", callback_data='suggestions'),
        InlineKeyboardButton("Новости", callback_data='news'),
        InlineKeyboardButton("Вопрос-Ответ", callback_data='faq')
    ]

    keyboard.add(*buttons)
    
    return keyboard