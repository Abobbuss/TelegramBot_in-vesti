import logging
import os
import dbinit, db_functions
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import Message
from datetime import datetime
from state import States
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from handlers import main_menu_handler

from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton

load_dotenv()
API_TOKEN = os.environ.get('TELEGRAM_TOKEN')
DB_PATH = os.environ.get('DB_PATH')
ADMIN = os.environ.get('ADMINS')


logging.basicConfig(level=logging.INFO)

storage = MemoryStorage()
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=storage)
dp.middleware.setup(LoggingMiddleware())


dp.register_message_handler(main_menu_handler.handle_start, commands=['start'])
dp.register_message_handler(main_menu_handler.process_name, state=States.waiting_for_name)
dp.register_message_handler(main_menu_handler.process_phone, state=States.waiting_for_phone)

@dp.callback_query_handler(lambda c: c.data == 'main_menu', state='*')
async def process_main_menu(callback_query: types.CallbackQuery, state: FSMContext):
    await States.main_menu.set()
    await callback_query.answer()
    await callback_query.message.edit_text("1Главное", reply_markup=main_menu())


@dp.callback_query_handler(lambda c: c.data == 'events', state='*')
async def process_events_menu(callback_query: types.CallbackQuery, state: FSMContext):
    await States.events.set()
    await callback_query.answer()
    await callback_query.message.edit_text("2Мероприятия", reply_markup=events(str(callback_query.from_user.id)))

@dp.callback_query_handler(lambda c: c.data == 'list_of_events', state='*')
async def process_list_of_events_menu(callback_query: types.CallbackQuery, state: FSMContext):
    await States.list_of_events.set()
    await callback_query.answer()
    list_of_events = db_functions.get_all_events()
    await callback_query.message.edit_text(list_of_events, reply_markup=news())

@dp.callback_query_handler(lambda c: c.data == 'sign_up_for_event', state='*')
async def process_sign_up_for_event_menu(callback_query: types.CallbackQuery, state: FSMContext):
    await States.sign_up_for_event.set()
    await callback_query.answer()
    list_of_events = db_functions.get_all_events()
    await callback_query.message.edit_text(list_of_events, reply_markup=sign_up_for_event(list_of_events))


@dp.callback_query_handler(lambda query: query.data.startswith("event_button:"), state='*')
async def handle_event_button(callback_query: types.CallbackQuery, state: FSMContext):
    await States.handle_event_button.set()
    event_id = int(callback_query.data.split(":")[1])
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("Записаться", callback_data=f"event_signup:{event_id}"))
    buttons = []
    if str(callback_query.from_user.id) in ADMIN:
        buttons.append(InlineKeyboardButton("Изменить", callback_data=f'edit_event:{event_id}'))
        buttons.append(InlineKeyboardButton("Удалить", callback_data=f'delete_event:{event_id}'))
    buttons.append(InlineKeyboardButton("Назад", callback_data='back'))
    keyboard.add(*buttons)
    await callback_query.message.edit_text(f"Информация о мероприятии:{event_id}", reply_markup=keyboard)


@dp.callback_query_handler(lambda query: query.data.startswith("event_signup:"), state='*')
async def handle_event_signup(callback_query: types.CallbackQuery, state: FSMContext):
    await States.handle_event_signup.set()
    event_id = int(callback_query.data.split(":")[1])
    user_id = callback_query.from_user.id

    db_functions.add_event_person_to_db(event_id, user_id)
    await States.main_menu.set()
    await callback_query.message.edit_text(f"Вы успешно записались на мероприятие!\n\n", reply_markup=main_menu())


@dp.callback_query_handler(lambda query: query.data.startswith("delete_event:"), state='*')
async def handle_delete_event(callback_query: types.CallbackQuery, state: FSMContext):
    await States.delete_event.set()
    event_id = int(callback_query.data.split(":")[1])
    if str(callback_query.from_user.id) in ADMIN:
        db_functions.delete_event_by_id(event_id)
    await callback_query.message.edit_text(f"Вы успешно удалили мероприятие!", reply_markup=main_menu())

@dp.callback_query_handler(lambda query: query.data.startswith("edit_event:"), state='*')
async def handle_edit_event(callback_query: types.CallbackQuery, state: FSMContext):
    await States.edit_event.set()
    event_id = int(callback_query.data.split(":")[1])
    await callback_query.message.edit_text(f"Выберите что вы хотите изменить", reply_markup=edit_event(event_id))

@dp.callback_query_handler(lambda query: query.data.startswith("edit_name:"), state='*')
async def handle_edit_name(callback_query: types.CallbackQuery, state: FSMContext):
    event_id = int(callback_query.data.split(":")[1])
    await States.edit_name.set()
    await state.update_data(event_id=event_id)
    await callback_query.message.edit_text("Введите новое название")

@dp.message_handler(state=States.edit_name)
async def process_suggestion(message: types.Message, state: FSMContext):
    new_name = message.text
    state_data = await state.get_data()
    event_id = state_data.get('event_id')
    if str(message.from_user.id) in ADMIN:
        db_functions.update_event_by_id(event_id, new_name=new_name)
    await message.answer("Вы успешно изменили название")



@dp.message_handler(state=States.waiting_for_suggestion)
async def process_suggestion(message: types.Message, state: FSMContext):
    suggestion = message.text

    db_functions.add_suggestion_to_db(message.chat.id, suggestion)

    await state.finish()

    await message.answer("Спасибо за предложение! Оно было успешно добавлено в базу данных.",  reply_markup=main_menu())

@dp.callback_query_handler(lambda query: query.data.startswith("back:"), state='*')
async def process_back_to_edit_event(callback_query: types.CallbackQuery, state: FSMContext):
    await States.edit_event.set()
    event_id = int(callback_query.data.split(":")[1])
    await callback_query.answer()
    await callback_query.message.edit_text('', reply_markup=edit_event(event_id))


@dp.callback_query_handler(lambda c: c.data == 'news', state='*')
async def process_news_menu(callback_query: types.CallbackQuery, state: FSMContext):
    await States.news.set()
    await callback_query.answer()
    await callback_query.message.edit_text("3НовостиРу", reply_markup=news())


@dp.callback_query_handler(lambda c: c.data == 'suggestions', state='*')
async def process_suggestions_menu(callback_query: types.CallbackQuery, state: FSMContext):
    await States.waiting_for_suggestion.set()
    await callback_query.answer()
    await callback_query.message.edit_text("Что бы вы предложили")






@dp.callback_query_handler(lambda c: c.data == 'faq', state='*')
async def process_faq_menu(callback_query: types.CallbackQuery, state: FSMContext):
    await States.faq.set()
    await callback_query.answer()
    await callback_query.message.edit_text("4вопрос-ответ", reply_markup=faq())


@dp.callback_query_handler(lambda c: c.data == 'back', state=(States.events, States.suggestions,
                                                              States.news, States.faq))
async def process_back(callback_query: types.CallbackQuery, state: FSMContext):
    await States.main_menu.set()
    await callback_query.answer()
    await callback_query.message.edit_text("Выберите действие:", reply_markup=main_menu())

@dp.callback_query_handler(lambda c: c.data == 'back', state=(States.list_of_events, States.sign_up_for_event))
async def process_back_to_events(callback_query: types.CallbackQuery, state: FSMContext):
    await States.events.set()
    await callback_query.answer()
    await callback_query.message.edit_text("Выберите действие:", reply_markup=events(str(callback_query.from_user.id)))

@dp.callback_query_handler(lambda c: c.data == 'back', state=States.handle_event_button)
async def process_back_to_events_from_description(callback_query: types.CallbackQuery, state: FSMContext):
    await States.sign_up_for_event.set()
    await callback_query.answer()
    list_of_events = db_functions.get_all_events()
    await callback_query.message.edit_text(list_of_events, reply_markup=sign_up_for_event(list_of_events))



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

def list_of_events():
    keyboard = InlineKeyboardMarkup(row_width=1)
    buttons = [
        InlineKeyboardButton("Записаться", callback_data='sign_up'),
        InlineKeyboardButton("Список мероприятии", callback_data='list_of_events'),
        InlineKeyboardButton("Назад", callback_data='back')
    ]
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

def sign_up_for_event(list):
    list_of_events = list
    keyboard = InlineKeyboardMarkup(row_width=1)
    buttons = [InlineKeyboardButton(f"Мероприятие: {event[1]}", callback_data=f'event_button:{event[0]}') for event in list_of_events]
    buttons.append(InlineKeyboardButton("Назад", callback_data='back'))
    # buttons = [
    #
    #     InlineKeyboardButton("Записаться", callback_data='sign_up'),
    #     InlineKeyboardButton("Список мероприятии", callback_data='list_of_events'),
    #     InlineKeyboardButton("Назад", callback_data='back')
    # ]
    keyboard.add(*buttons)
    return keyboard

def suggestions():
    keyboard = InlineKeyboardMarkup(row_width=1)
    buttons = [
        InlineKeyboardButton("ввод данных", callback_data='add_suggestion'),
        InlineKeyboardButton("Назад", callback_data='back')
    ]
    keyboard.add(*buttons)
    return keyboard

def news():
    keyboard = InlineKeyboardMarkup(row_width=1)
    buttons = [
        InlineKeyboardButton("Назад", callback_data='back')
    ]
    keyboard.add(*buttons)
    return keyboard

def faq():
    keyboard = InlineKeyboardMarkup(row_width=1)
    buttons = [
        InlineKeyboardButton("Вопрос1", callback_data='question1'),
        InlineKeyboardButton("Вопрос2", callback_data='question2'),
        InlineKeyboardButton("Вопрос3", callback_data='question3'),
        InlineKeyboardButton("Вопрос4", callback_data='question4'),
        InlineKeyboardButton("Назад", callback_data='back')
    ]
    keyboard.add(*buttons)
    return keyboard

if __name__ == '__main__':
    if not os.path.exists(DB_PATH):
        dbinit.create_bd()
    executor.start_polling(dp, skip_updates=False)