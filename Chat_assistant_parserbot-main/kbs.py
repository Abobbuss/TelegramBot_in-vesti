from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton
import os

ADMIN = os.environ.get('ADMINS')

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

def events(user_id):
    keyboard = InlineKeyboardMarkup(row_width=1)
    buttons = [
        InlineKeyboardButton("Записаться", callback_data='sign_up_for_event'),
        InlineKeyboardButton("Список мероприятии", callback_data='list_of_events'),

    ]
    if user_id in ADMIN:
        buttons.append(InlineKeyboardButton("Добавить мероприятие", callback_data='back'))
    buttons.append(InlineKeyboardButton("Назад", callback_data='back'))
    keyboard.add(*buttons)
    return keyboard