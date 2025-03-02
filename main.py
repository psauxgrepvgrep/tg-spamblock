import logging
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message, ChatMemberAdministrator
from db import increment_keyword_frequency, is_keyword_in_db, add_keyword_to_db, get_all_keywords
from dotenv import load_dotenv
import os

load_dotenv()
API_TOKEN = os.getenv('BOT_TOKEN')
if not API_TOKEN:
    raise ValueError("BOT_TOKEN не найден в переменных окружения или файле .env")
logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# Обработчик команды /ban
@dp.message(Command('ban'), F.reply_to_message.as_("replied_message"))
async def handle_ban_command(message: Message, replied_message: Message):
    try:
        chat_member = await bot.get_chat_member(chat_id=message.chat.id, user_id=message.from_user.id)

        if isinstance(chat_member, ChatMemberAdministrator) or message.sender_chat.id == message.chat.id:
            if replied_message.text:
                words = replied_message.text.lower().split()  # Разделяем сообщение на слова
                added_keywords = []

                for word in words:
                    if not is_keyword_in_db(word.strip()):
                        add_keyword_to_db(word.strip())
                        added_keywords.append(word.strip())

                if added_keywords:
                    await message.reply(f"Добавлены запрещенные слова: {', '.join(added_keywords)}")
                else:
                    await message.reply("Нет новых слов для добавления.")
                await replied_message.delete()
                await message.delete()
            else:
                await message.reply("Ответьте на сообщение с текстом, чтобы добавить запрещенные слова.")
        else:
            await message.reply("Вы не являетесь администратором группы.")
    except Exception as e:
        logging.error(f"Ошибка при проверке прав администратора: {e}")
        await message.reply("Не удалось проверить ваши права. Убедитесь, что бот является администратором группы.")

# Обработчик сообщений
@dp.message(F.text)
async def handle_message(message: Message):
    words = message.text.lower().split()
    total_words = len(words)
    banned_words_count = 0

    banned_keywords = get_all_keywords()

    for word in words:
        if word in banned_keywords:
            banned_words_count += 1
            increment_keyword_frequency(word)

    if total_words > 0 and (banned_words_count / total_words) >= 0.8:
        await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
        await bot.send_message(chat_id=message.chat.id, text=f"Сообщение удалено: {message.text} (из-за попадания в спам-фильтр).")
    elif banned_words_count > 0:
        await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
        await bot.send_message(chat_id=message.chat.id, text=f"Сообщение удалено: {message.text} (из-за попадания в спам-фильтр).")

# Основная функция
async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())