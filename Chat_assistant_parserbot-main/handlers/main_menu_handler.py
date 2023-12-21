from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command
from aiogram.types import CallbackQuery
from state import States
import kbs
import db_functions


async def handle_start(message: types.Message, state: FSMContext):
    existing_person = db_functions.find_person_in_db(message.chat.id)

    if not existing_person:
        await States.waiting_for_name.set()

        await message.answer("Добро пожаловать! Для начала, давайте узнаем ваши ФИО.")
    else:
        await States.main_menu.set()

        await message.answer("Привет! Выберите действие:", reply_markup=kbs.main_menu())

        await States.contact.set()