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
from myState import States
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from handlers import events_handler, main_menu_handler, FAQ_handler


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

dp.register_callback_query_handler(events_handler.process_events_menu, lambda c: c.data == 'events', state='*')
dp.register_callback_query_handler(events_handler.handle_event_button, lambda query: query.data.startswith("event_button:"), state='*')
dp.register_callback_query_handler(events_handler.handle_event_signup, lambda query: query.data.startswith("event_signup:"), state='*')
dp.register_callback_query_handler(events_handler.handle_event_signout, lambda query: query.data.startswith("event_signout:"), state='*')
dp.register_callback_query_handler(events_handler.handle_add_event, lambda query: query.data.startswith("add_event"), state='*')
dp.register_callback_query_handler(events_handler.handle_active_person_event, lambda query: query.data.startswith("active_person_event"), state='*')
dp.register_message_handler(events_handler.handle_add_event_waiting_name, state=States.add_event_waiting_name)
dp.register_message_handler(events_handler.handle_add_event_waiting_date, state=States.add_event_waiting_date)
dp.register_message_handler(events_handler.handle_add_event_waiting_description, state=States.add_event_waiting_description)
dp.register_callback_query_handler(events_handler.handle_edit_event, lambda query: query.data.startswith("edit_event:"), state='*')
dp.register_callback_query_handler(events_handler.handle_delete_event, lambda query: query.data.startswith("delete_event:"), state='*')
dp.register_callback_query_handler(events_handler.handle_list_of_event_people, lambda query: query.data.startswith("list_of_event_people:"), state='*')

dp.register_callback_query_handler(FAQ_handler.show_faq, lambda c: c.data.startswith('faq') and not c.data.startswith('faq_next') 
                                   and not c.data.startswith('faq_prev') and not c.data.startswith('faq_answer'), state='*')
dp.register_callback_query_handler(FAQ_handler.faq_pagination, lambda c: c.data.startswith('faq_next') or c.data.startswith('faq_prev'), state='*')
dp.register_callback_query_handler(FAQ_handler.show_answer_faq, lambda c: c.data.startswith('faq_answer:'), state='*')
dp.register_callback_query_handler(FAQ_handler.back_to_faq, lambda c: c.data.startswith('back_to_faq:'), state='*')

dp.register_callback_query_handler(main_menu_handler.main_menu, lambda c: c.data == 'back_to_main_menu', state='*')


@dp.callback_query_handler(lambda query: query.data.startswith("delete_event:"), state='*')
async def handle_delete_event(callback_query: types.CallbackQuery, state: FSMContext):
    await States.delete_event.set()
    event_id = int(callback_query.data.split(":")[1])
    if str(callback_query.from_user.id) in ADMIN:
        db_functions.delete_event_by_id(event_id)
    await callback_query.message.edit_text(f"Вы успешно удалили мероприятие!", reply_markup=main_menu())

# @dp.callback_query_handler(lambda query: query.data.startswith("edit_event:"), state='*')
# async def handle_edit_event(callback_query: types.CallbackQuery, state: FSMContext):
#     await States.edit_event.set()
#     event_id = int(callback_query.data.split(":")[1])
#     await callback_query.message.edit_text(f"Выберите что вы хотите изменить", reply_markup=edit_event(event_id))

# @dp.callback_query_handler(lambda query: query.data.startswith("edit_name:"), state='*')
# async def handle_edit_name(callback_query: types.CallbackQuery, state: FSMContext):
#     event_id = int(callback_query.data.split(":")[1])
#     await States.edit_name.set()
#     await state.update_data(event_id=event_id)
#     await callback_query.message.edit_text("Введите новое название")

# @dp.message_handler(state=States.edit_name)
# async def process_suggestion(message: types.Message, state: FSMContext):
#     new_name = message.text
#     state_data = await state.get_data()
#     event_id = state_data.get('event_id')
#     if str(message.from_user.id) in ADMIN:
#         db_functions.update_event_by_id(event_id, new_name=new_name)
#     await message.answer("Вы успешно изменили название")



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


# @dp.callback_query_handler(lambda c: c.data == 'news', state='*')
# async def process_news_menu(callback_query: types.CallbackQuery, state: FSMContext):
#     await States.news.set()
#     await callback_query.answer()
#     await callback_query.message.edit_text("3НовостиРу", reply_markup=news())


@dp.callback_query_handler(lambda c: c.data == 'suggestions', state='*')
async def process_suggestions_menu(callback_query: types.CallbackQuery, state: FSMContext):
    await States.waiting_for_suggestion.set()
    await callback_query.answer()
    await callback_query.message.edit_text("Что бы вы предложили")

# @dp.callback_query_handler(lambda c: c.data == 'faq', state='*')
# async def process_faq_menu(callback_query: types.CallbackQuery, state: FSMContext):
#     await States.faq.set()
#     await callback_query.answer()
#     await callback_query.message.edit_text("4вопрос-ответ", reply_markup=faq())


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


if __name__ == '__main__':
    if not os.path.exists(DB_PATH): 
        dbinit.create_bd()
    executor.start_polling(dp, skip_updates=False)

