from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton
import os
import db_functions
from dotenv import load_dotenv


load_dotenv()
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



def event_button(list, user_id):
    list_of_events = list
    keyboard = InlineKeyboardMarkup(row_width=1)
    buttons = [InlineKeyboardButton(f"{event[1]}", callback_data=f'event_button:{event[0]}') for event in list_of_events]
    if str(user_id) in ADMIN:
        buttons.append(InlineKeyboardButton("Добавить мероприятие", callback_data='add_event'))
        buttons.append(InlineKeyboardButton("Активные участники", callback_data='active_person_event'))
    buttons.append(InlineKeyboardButton("Назад", callback_data='back_to_main_menu'))

    
    keyboard.add(*buttons)
    return keyboard

def event(event_id, user_id):
    keyboard = InlineKeyboardMarkup()

    user_id_bd = db_functions.find_person_in_db(user_id)[0][0]

    if (db_functions.find_event_person_by_id(user_id_bd, event_id) is None):
        keyboard.add(InlineKeyboardButton("Записаться", callback_data=f"event_signup:{event_id}"))
    else:
        keyboard.add(InlineKeyboardButton("Отменить запись", callback_data=f"event_signout:{event_id}"))

    buttons = []
    if str(user_id) in ADMIN:
        buttons.append(InlineKeyboardButton("Изменить", callback_data=f'edit_event:{event_id}'))
        buttons.append(InlineKeyboardButton("Удалить", callback_data=f'delete_event:{event_id}'))
        buttons.append(InlineKeyboardButton("Участники", callback_data=f'list_of_event_people:{event_id}'))
    keyboard.add(InlineKeyboardButton("Назад", callback_data='events'))
    
    keyboard.add(*buttons)
    return keyboard

def edit_event(event_id):
    keyboard = InlineKeyboardMarkup(row_width=1)
    buttons = [
        InlineKeyboardButton("Изменить название", callback_data=f'edit_name:{event_id}'),
        InlineKeyboardButton("Изменить дату", callback_data=f'edit_date:{event_id}'),
        InlineKeyboardButton("Изменить описание", callback_data=f'edit_description:{event_id}'),
        InlineKeyboardButton("Назад", callback_data=f'back:{event_id}')
    ]
    keyboard.add(*buttons)
    return keyboard



def faq(qa_data, start_index=0, limit=5):
    keyboard = InlineKeyboardMarkup(row_width=1)

    qa_data_slice = qa_data[start_index: start_index + limit]
    buttons = []

    for idx, (qa_id, question, answer_type, answer) in enumerate(qa_data_slice, start=1):
        callback_data = f'faq_answer:{qa_id}'
        button = InlineKeyboardButton(f"{question}", callback_data=callback_data)
        keyboard.add(button)

    if start_index + limit < len(qa_data):
        next_index = start_index + limit
        callback_data_next = f'faq_next_{next_index}'
        buttons.append(InlineKeyboardButton("Дальше", callback_data=callback_data_next))

    if start_index > 0:
        prev_index = max(0, start_index - limit)
        callback_data_prev = f'faq_prev_{prev_index}'
        buttons.append(InlineKeyboardButton("Назад", callback_data=callback_data_prev))

    keyboard.add(*buttons)

    keyboard.add(InlineKeyboardButton("Главное меню", callback_data='back_to_main_menu'))

    return keyboard