import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
from config_reader import config

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

# Хэндлер на команду /lol
@dp.message(Command("lol"))
async def cmd_lol(message: types.Message):
    await message.answer("Lol!")

@dp.message(Command("lmao"))
async def cmd_lmao(message: types.Message):
    await message.answer("Lmao!")

@dp.message(Command("trash"))
async def cmd_trash(message: types.Message):
    await message.answer("Trash!")

# Запуск процесса поллинга новых апдейтов
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())