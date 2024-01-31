import asyncio
from aiogram import Dispatcher, types
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
from aiogram import Bot
from dotenv import load_dotenv
from aiogram.contrib.fsm_storage.memory import MemoryStorage

load_dotenv()
API_TOKEN = os.environ.get('TELEGRAM_TOKEN')
bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

async def show_faq(callback_query: types.CallbackQuery):
    qa_data = db_functions.get_all_qa()
    
    await callback_query.message.edit_text("Список вопросов:", reply_markup=kbs.faq(qa_data, start_index=0))


async def faq_pagination(callback_query: types.CallbackQuery):
    data_parts = callback_query.data.split('_')

    current_index = int(data_parts[2])

    qa_data = db_functions.get_all_qa()

    await callback_query.message.edit_text("Вот список вопросов:", reply_markup=kbs.faq(qa_data, start_index=current_index))

async def show_answer_faq(callback_query: types.CallbackQuery):
    qa_id = int(callback_query.data.split(':')[-1])

    answer = db_functions.get_answer_by_id(qa_id)
    answer_type = answer[0][2]

    keyboard_for_text = InlineKeyboardMarkup(row_width=1)
    button_for_text = InlineKeyboardButton("Назад", callback_data='faq:')
    keyboard_for_text.add(button_for_text)
    
    if answer_type == 'text':
            await callback_query.message.edit_text(f"Решение:\n{answer[0][3]}", reply_markup=keyboard_for_text)

    elif answer_type == 'video':
        script_dir = os.path.dirname(os.path.abspath(__file__))
        path_dir = "video_answer"
        video_dir = os.path.join(script_dir, path_dir)
        file_name = answer[0][3]
        video_answer_dir = os.path.join(video_dir, file_name)

        if os.path.exists(video_answer_dir): 
            with open(video_answer_dir, 'rb') as video_file:
                sent_message = await bot.send_video(callback_query.from_user.id, video_file)

                sent_message_id = sent_message.message_id
                keyboard_for_video = InlineKeyboardMarkup(row_width=1)
                button_for_video = InlineKeyboardButton("Назад", callback_data=f'back_to_faq:{sent_message_id}')
                keyboard_for_video.add(button_for_video)

                await callback_query.message.edit_text("В этом видео вы сможете найти свой ответ!",  reply_markup=keyboard_for_video)
        else:
            await callback_query.message.edit_text("Произошла ошибка\nПовторите позже", reply_markup=keyboard_for_text)
    else:
        await callback_query.message.edit_text("Произошла ошибка:\nПовторите позжеq", reply_markup=keyboard_for_text)

async def back_to_faq(callback_query: types.CallbackQuery):
    sent_message_id = int(callback_query.data.split(':')[-1])

    try:
        await bot.delete_message(callback_query.from_user.id, sent_message_id)
    except Exception as e:
        print(f"Ошибка при удалении сообщения: {e}")
    
    qa_data = db_functions.get_all_qa()
    
    await callback_query.message.edit_text("Список вопросов:", reply_markup=kbs.faq(qa_data, start_index=0))
