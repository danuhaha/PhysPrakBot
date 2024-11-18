import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters.command import Command
from config_reader import config
from aiogram.types import Message, ContentType, ReplyKeyboardMarkup, KeyboardButton, WebAppInfo, BufferedInputFile
from aiogram.utils.keyboard import InlineKeyboardBuilder
from random import *
import indirect_error

# Включаем логирование, чтобы не пропустить важные сообщения
logging.basicConfig(level=logging.INFO)
# Объект бота
bot = Bot(token=config.bot_token.get_secret_value())
# Диспетчер
dp = Dispatcher()


# Хэндлер на команду /start
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Hello!")


@dp.message(Command("random"))
async def cmd_help(message: types.Message):
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(text="Нажми меня", callback_data="random_value"))
    await message.answer("Select help", reply_markup=builder.as_markup())


@dp.callback_query(F.data == "random_value")
async def send_random_value(callback: types.CallbackQuery):
    await callback.message.answer(str(randint(1, 10)))


@dp.message(Command("hello"))
async def cmd_hello(message: types.Message):
    await message.answer(f"Hello, {message.from_user.full_name}!")


@dp.message(F.content_type == ContentType.WEB_APP_DATA)
async def handle_web_app_data(message: Message):
    latex_input, uncertain_vars = message.web_app_data.data.split(';')

    total_uncertainty = indirect_error.compute_uncertainty(latex_input, uncertain_vars)

    buffer_image = indirect_error.visualize_latex(total_uncertainty)

    with buffer_image as image:
        result = await message.answer_photo(
            BufferedInputFile(
                image.read(),
                filename="image from buffer.jpg"
            )
        )


@dp.message(Command("webapp"))
async def send_welcome(message: types.Message):
    # Create a keyboard with a button that opens the web app
    kb = [
        [KeyboardButton(text="Open Web App", web_app=WebAppInfo(url='https://danuhaha.github.io/PhysPrakBotWebApp/'))]]
    keyboard = ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True, input_field_placeholder="лол")

    # Send a message with the keyboard
    await message.answer("Click the button below to open the web app:", reply_markup=keyboard)


# Запуск процесса поллинга новых апдейтов
async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
