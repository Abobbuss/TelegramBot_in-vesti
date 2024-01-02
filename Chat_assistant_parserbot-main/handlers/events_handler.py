from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command
from aiogram.types import CallbackQuery
from state import States
import kbs
import db_functions
import os


async def process_events_menu(callback_query: types.CallbackQuery, state: FSMContext):
    await States.events.set()
    print(2)
    await callback_query.answer()
    await callback_query.message.edit_text("2Мероприятия", reply_markup=kbs.events(str(callback_query.from_user.id)))