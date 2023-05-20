import asyncio
import aiohttp
import config
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor

# Ваш токен Telegram бота, в преременной config
bot = (config.TOKEN)

# Создаем экземпляры бота и диспетчера
bot = Bot(token=bot)
dp = Dispatcher(bot)

# Список URL для проверки
urls = {}

# Функция для проверки статуса сервера
async def check_url(url):
    async with aiohttp.ClientSession() as session:
        async with session.head(url) as resp:
            status = resp.status
            return {'url': url, 'status': status}

# Функция для проверки URL
async def check_urls():
    results = await asyncio.gather(*[check_url(url) for url in urls.keys()])

    message_lines = []
    for result in results:
        line = f"{result['url']} - Статус: {result['status']}"
        message_lines.append(line)

    if message_lines:
        message = '\n'.join(message_lines)

        # Отправка сообщения со списком URL и статус кодом
        for chat_id in set(urls.values()):
            await bot.send_message(chat_id, message)

# Команда /start
@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    await message.reply('Я бот для проверки статуса сервера по URL каждый час. Отправьте /add <URL> для добавления в список проверки.')

# Команда /add
@dp.message_handler(commands=['add'])
async def add_url_command(message: types.Message):
    args = message.get_args()
    if args:
        urls[args] = message.chat.id
        await message.reply(f'Ссылка {args} добавлена.')
    else:
        await message.reply('Пожалуйста, укажите URL.')

# Команда /remove
@dp.message_handler(commands=['remove'])
async def remove_url_command(message: types.Message):
    args = message.get_args()
    if args in urls:
        del urls[args]
        await message.reply(f'Ссылка {args} удалена из списка.')
    else:
        await message.reply(f'Ссылка {args} не найдена в списке.')

# Команда /list
@dp.message_handler(commands=['list'])
async def list_urls_command(message: types.Message):
    if urls:
        url_list = '\n'.join(urls.keys())
        await message.reply(f'Список URL:\n{url_list}')
    else:
        await message.reply('Список URL пуст.')

# Функция для запуска периодической проверки URL ссылок
async def start_checking():
    while True:
        await check_urls()
        await asyncio.sleep(3600)

# Запуск бота
if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.create_task(start_checking())
    executor.start_polling(dp, skip_updates=True)
