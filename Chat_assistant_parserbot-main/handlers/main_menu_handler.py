from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command
from aiogram.types import CallbackQuery
from myState import States
import kbs
import db_functions
import os


exception_message = os.environ.get('EXCEPTION_MESSAGE')

async def handle_start(message: types.Message, state: FSMContext):
    try:
        existing_person = db_functions.find_person_in_db(message.chat.id)

        if not existing_person:
            await States.waiting_for_name.set()
            await message.answer("Добро пожаловать! Для начала, давайте узнаем ваши ФИО.")
        else:
            await States.main_menu.set()
            await message.answer("Привет! Выберите действие:", reply_markup=kbs.main_menu())

    except Exception as e:
        await message.answer(exception_message)

async def process_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)

    await message.answer(f"Спасибо, {message.text}! Теперь укажите ваш номер телефона.")

    await States.waiting_for_phone.set()

async def process_phone(message: types.Message, state: FSMContext):
    try:
        await state.update_data(phone=message.text)

        user_data = await state.get_data()

        user_id = message.from_user.id
        name = user_data.get('name')
        phone = user_data.get('phone')

        db_functions.add_person_to_db(user_id, name, phone)

        await state.finish()

        await States.main_menu.set()
        await message.answer("Спасибо за регистрацию! ", reply_markup=kbs.main_menu())
    except Exception as e:
        await message.answer(exception_message)

async def main_menu(callback_query: types.CallbackQuery, state: FSMContext):
    await States.main_menu.set()
    await callback_query.message.edit_text("Выберите действие:", reply_markup=kbs.main_menu())