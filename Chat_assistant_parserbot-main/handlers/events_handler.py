from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command
from aiogram.types import CallbackQuery
from myState import States
import kbs
import db_functions
import os
from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton



async def process_events_menu(callback_query: types.CallbackQuery, state: FSMContext):
    await States.events.set()
    await callback_query.answer()

    list_of_events = db_functions.get_all_events()

    await callback_query.message.edit_text("Наши мероприятия", reply_markup=kbs.event_button(list_of_events, callback_query.message.chat.id))

async def handle_event_button(callback_query: types.CallbackQuery, state: FSMContext):
    await States.handle_event_button.set()

    event_id = int(callback_query.data.split(":")[1])
    event_name = db_functions.get_event(event_id)[0][1]
    event_date = db_functions.get_event(event_id)[0][2]
    event_description = db_functions.get_event(event_id)[0][3]

    await callback_query.message.edit_text(f"Мероприятие: {event_name}\nДата: {event_date}\nИнформация о мероприятии:\n{event_description}", reply_markup=kbs.event(event_id, callback_query.message.chat.id))

async def handle_event_signup(callback_query: types.CallbackQuery, state: FSMContext):
    await States.handle_event_signup.set()

    event_id = int(callback_query.data.split(":")[1])
    user_id = db_functions.find_person_in_db(callback_query.from_user.id)[0][0]

    db_functions.add_event_person_to_db(event_id, user_id)

    list_of_events = db_functions.get_all_events()

    await States.events.set()
    await callback_query.message.edit_text(f"Вы успешно записались на мероприятие!\n\n", reply_markup=kbs.event_button(list_of_events, callback_query.message.chat.id))

async def handle_event_signout(callback_query: types.CallbackQuery, state: FSMContext):
    await States.handle_event_signout.set()

    event_id = int(callback_query.data.split(":")[1])
    user_id = db_functions.find_person_in_db(callback_query.from_user.id)[0][0]

    event_person_id = db_functions.find_event_person_by_id(user_id, event_id)
    db_functions.delete_event_person_by_id(event_person_id)

    list_of_events = db_functions.get_all_events()

    await States.events.set()
    await callback_query.message.edit_text(f"Вы отменили свою запись на мероприятие:(\n\n", reply_markup=kbs.event_button(list_of_events, callback_query.message.chat.id))

# admin

async def handle_add_event(callback_query: types.CallbackQuery, state: FSMContext):
    await States.add_event_waiting_name.set()
    await callback_query.message.edit_text("Введите название мероприятия, которое хотите добавить")
    

async def handle_add_event_waiting_name(message: types.Message, state: FSMContext):
    await state.update_data(event_name=message.text)

    await States.add_event_waiting_date.set()
    await message.answer(f"Название - {message.text}!\nТеперь укажите дату меропрития.")

async def handle_add_event_waiting_date(message: types.Message, state: FSMContext):
    await state.update_data(event_date=message.text)

    await States.add_event_waiting_description.set()
    await message.answer(f"Дата - {message.text}!\nТеперь укажите описание меропрития.")

async def handle_add_event_waiting_description(message: types.Message, state: FSMContext):
    await state.update_data(event_description=message.text)

    await States.events.set()
    await message.answer(f"Описание - {message.text}!\nМероприятие добавлено!.")

    user_data = await state.get_data()

    event_name = user_data.get('event_name')
    event_date = user_data.get('event_date')
    event_description = user_data.get('event_description')
    db_functions.add_event_to_db(event_name, event_date, event_description)

    list_of_events = db_functions.get_all_events()

    await States.events.set()
    await message.answer(f"Теперь вот так выглядит список мероприятий\n\n", reply_markup=kbs.event_button(list_of_events, message.chat.id))


async def handle_edit_event(callback_query: types.CallbackQuery, state: FSMContext):
    list_of_events = db_functions.get_all_events()

    await callback_query.message.edit_text(f"Тут будет изменения мероприятия, чуть позже сделаю", reply_markup=kbs.event_button(list_of_events, callback_query.message.chat.id))
    # await States.edit_event.set()
    # event_id = int(callback_query.data.split(":")[1])
    # await callback_query.message.edit_text(f"Выберите что вы хотите изменить", reply_markup=kbs.edit_event(event_id))


async def handle_delete_event(callback_query: types.CallbackQuery, state: FSMContext):
    await States.delete_event.set()

    event_id = int(callback_query.data.split(":")[1])
    db_functions.delete_event_by_id(event_id)
    await callback_query.message.edit_text(f"Вы успешно удалили мероприятие!", reply_markup=kbs.main_menu())

async def handle_list_of_event_people(callback_query: types.CallbackQuery, state: FSMContext):
    await States.list_of_event_people.set()

    event_id = int(callback_query.data.split(":")[1])
    people_data = db_functions.get_all_people_of_event(event_id)

    if not people_data:
        await callback_query.message.edit_text("На мероприятии нет участников.", reply_markup=kbs.main_menu())
    else:
        people_ids = [person[2] for person in people_data]

        people_info = []
        for person_id in people_ids:
            person_data = db_functions.get_info_about_person(person_id)
            if person_data:
                person_name = person_data[0][2]
                people_info.append(person_name)

        message_text = f"На мероприятии {len(people_info)} участников:\n" + "\n".join(people_info)
        await callback_query.message.edit_text(message_text, reply_markup=kbs.main_menu())

async def handle_active_person_event(callback_query: types.CallbackQuery, state: FSMContext):
    active_list = db_functions.get_active_people()
    print(active_list)
    keyboard = InlineKeyboardMarkup(row_width=1)
    buttons = [
        InlineKeyboardButton("Назад", callback_data='events')
    ]
    keyboard.add(*buttons)

    active_people_text = "\n".join([f"{person[0]}: {person[1]}" for person in active_list])
    await callback_query.message.edit_text(f"Вот список активности работников по количеству мероприятий:\n{active_people_text}", reply_markup=keyboard)