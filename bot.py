import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters.command import Command
from config_reader import config
from aiogram.types import Message, ContentType, ReplyKeyboardMarkup, KeyboardButton, WebAppInfo, BufferedInputFile, \
    ReplyKeyboardRemove
from aiogram.utils.keyboard import InlineKeyboardBuilder
from random import *
import indirect_error

logging.basicConfig(level=logging.INFO)
bot = Bot(token=config.bot_token.get_secret_value())
dp = Dispatcher()


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Привет! Чтобы рассчитать погрешность, вызови команду /error")


@dp.message(Command("random"))
async def cmd_help(message: types.Message):
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(text="Нажми меня", callback_data="random_value"))
    await message.answer("Генератор рандомных чисел", reply_markup=builder.as_markup())


@dp.callback_query(F.data == "random_value")
async def send_random_value(callback: types.CallbackQuery):
    await callback.message.answer(str(randint(1, 10)))


@dp.message(F.content_type == ContentType.WEB_APP_DATA)
async def handle_web_app_data(message: Message):
    latex_input, uncertain_vars = message.web_app_data.data.split(';')

    total_uncertainty = indirect_error.compute_uncertainty(latex_input, uncertain_vars)

    buffer_image = indirect_error.visualize_latex(total_uncertainty)

    with buffer_image as image:
        await message.answer_photo(
            BufferedInputFile(
                image.read(),
                filename="image from buffer.jpg"
            ), reply_markup=ReplyKeyboardRemove()
        )


@dp.message(Command("error"))
async def cmd_error(message: types.Message):
    kb = [
        [KeyboardButton(text="Рассчитать погрешность",
                        web_app=WebAppInfo(url='https://physprak.bot.nu'))]]
    keyboard = ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True, one_time_keyboard=True,
                                   input_field_placeholder="Воспользуйся кнопкой ниже")

    await message.answer("Нажми на кнопку ниже, чтобы рассчитать погрешность", reply_markup=keyboard)


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
