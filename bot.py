import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters.command import Command
from config_reader import config
from aiogram.types import Message, ContentType, ReplyKeyboardMarkup, KeyboardButton, WebAppInfo, BufferedInputFile, \
    CallbackQuery
from aiogram.client.default import DefaultBotProperties
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.enums import ParseMode
import indirect_error

logging.basicConfig(level=logging.INFO)
bot = Bot(token=config.bot_token.get_secret_value(), default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

# Temporary data storage
temp_data = {}
# Timeout for data (in seconds)
DATA_TIMEOUT = 600  # 10 minutes


async def remove_data_after_timeout(user_id):
    await asyncio.sleep(DATA_TIMEOUT)
    temp_data.pop(user_id, None)


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Привет! Чтобы рассчитать погрешность, вызови команду /error")


@dp.callback_query()
async def handle_inline_button(query: CallbackQuery):
    user_id = query.from_user.id

    await query.message.edit_reply_markup(reply_markup=None)

    if query.data == "new":
        await query.message.bot.send_message(
            chat_id=query.message.chat.id,
            text="Starting new process..."
        )
        # Handle new logic here
    elif query.data == "menu":
        await query.message.bot.send_message(
            chat_id=query.message.chat.id,
            text="Returning to menu..."
        )
        # Handle menu logic here
    elif query.data == "edit":
        if user_id in temp_data:
            data = temp_data[user_id]

            await query.message.bot.send_message(
                chat_id=query.message.chat.id,
                text=f"Editing data: {data['latex_input']} and {data['uncertain_vars']}")

            # Handle edit logic here
        else:
            await query.message.bot.send_message(
                chat_id=query.message.chat.id,
                text="Data expired or not found."
            )
    # Delete data after processing
    del temp_data[user_id]


@dp.message(F.content_type == ContentType.WEB_APP_DATA)
async def handle_web_app_data(message: Message):
    latex_input, uncertain_vars_input = message.web_app_data.data.split(';')

    total_uncertainty_latex = indirect_error.compute_uncertainty(latex_input, uncertain_vars_input)

    user_id = message.from_user.id
    temp_data[user_id] = {
        "latex_input": latex_input,
        "uncertain_vars": uncertain_vars_input,
    }

    # Schedule data removal after timeout
    asyncio.create_task(remove_data_after_timeout(user_id))

    # Inline keyboard with Edit and New buttons
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(text="Редактировать", callback_data="edit"),
                types.InlineKeyboardButton(text="Новый расчет", callback_data="new"),
                types.InlineKeyboardButton(text="Меню", callback_data="menu"))
    reply_markup = builder.as_markup()

    buffer_image_initial = indirect_error.visualize_latex(
        f"${latex_input}$" + r"$\, , \,$" + f"${uncertain_vars_input}$")

    with buffer_image_initial as image:
        await message.answer_photo(
            BufferedInputFile(
                image.read(),
                filename="image from buffer.jpg"
            ), caption="<b>Формула и переменные с погрешностью</b>",
            show_caption_above_media=True
        )
    buffer_image_uncertainty = indirect_error.visualize_latex(f"${total_uncertainty_latex}$")

    with buffer_image_uncertainty as image:
        await message.answer_photo(
            BufferedInputFile(
                image.read(),
                filename="image from buffer.jpg"
            ), caption="<b>Косвенная погрешность</b>",
            show_caption_above_media=True,
            reply_markup=reply_markup
        )


@dp.message(Command("error"))
async def cmd_error(message: types.Message):
    kb = [
        [KeyboardButton(text="Рассчитать погрешность",
                        web_app=WebAppInfo(url='https://iluvurmom.servebeer.com'))]]
    keyboard = ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True, one_time_keyboard=True,
                                   input_field_placeholder="Воспользуйся кнопкой ниже")

    await message.answer("Нажми на кнопку ниже, чтобы рассчитать погрешность", reply_markup=keyboard)


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
