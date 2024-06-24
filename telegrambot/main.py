import asyncio
from aiohttp import web
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler

# Указываем ID чата администратора
ADMIN_CHAT_ID = '794780600'

# Список заблокированных пользователей
blocked_users = []

# Обработка команды /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if str(update.message.chat_id) == ADMIN_CHAT_ID:
        keyboard = [
            [InlineKeyboardButton("Просмотреть заблокированных пользователей", callback_data='view_blocked')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text('Добро пожаловать, администратор! Выберите действие:', reply_markup=reply_markup)
    else:
        await update.message.reply_text('Привет! Я бот для обратной связи. Чтобы связаться с администратором, просто отправьте сообщение.')

# Обработка всех текстовых сообщений
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.chat_id
    if user_id in blocked_users:
        await update.message.reply_text('Вы заблокированы и не можете отправлять сообщения.')
        return
    await update.message.reply_text('Ваше сообщение отправлено администратору. Спасибо за обратную связь!')
    await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=f'Сообщение от пользователя {user_id}:\n{update.message.text}')

# Обработка отправки фото
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.chat_id
    if user_id in blocked_users:
        await update.message.reply_text('Вы заблокированы и не можете отправлять сообщения.')
        return
    photo = update.message.photo[-1]
    file = await photo.get_file()
    await file.download_to_drive(f'{user_id}_photo.jpg')
    await update.message.reply_text('Ваше фото отправлено администратору. Спасибо за обратную связь!')
    await context.bot.send_photo(chat_id=ADMIN_CHAT_ID, photo=open(f'{user_id}_photo.jpg', 'rb'), caption=f'Фото от пользователя {user_id}')

# Обработка отправки видео
async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.chat_id
    if user_id in blocked_users:
        await update.message.reply_text('Вы заблокированы и не можете отправлять сообщения.')
        return
    video = update.message.video
    file = await video.get_file()
    await file.download_to_drive(f'{user_id}_video.mp4')
    await update.message.reply_text('Ваше видео отправлено администратору. Спасибо за обратную связь!')
    await context.bot.send_video(chat_id=ADMIN_CHAT_ID, video=open(f'{user_id}_video.mp4', 'rb'), caption=f'Видео от пользователя {user_id}')

# Обработка отправки файлов
async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.chat_id
    if user_id in blocked_users:
        await update.message.reply_text('Вы заблокированы и не можете отправлять сообщения.')
        return
    document = update.message.document
    file = await document.get_file()
    await file.download_to_drive(f'{user_id}_{document.file_name}')
    await update.message.reply_text('Ваш файл отправлен администратору. Спасибо за обратную связь!')
    await context.bot.send_document(chat_id=ADMIN_CHAT_ID, document=open(f'{user_id}_{document.file_name}', 'rb'), caption=f'Файл от пользователя {user_id}')

# Обработка команды /reply
async def reply(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if str(update.message.chat_id) == ADMIN_CHAT_ID:
        args = context.args
        if len(args) < 2:
            await update.message.reply_text('Использование: /reply <user_id> <message>')
            return
        user_id = args[0]
        reply_message = ' '.join(args[1:])
        await context.bot.send_message(chat_id=user_id, text=f'Ответ от администратора:\n{reply_message}')
        await update.message.reply_text('Ваш ответ отправлен пользователю.')
    else:
        await update.message.reply_text('Эта команда доступна только администратору.')

# Обработка команды /block
async def block(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if str(update.message.chat_id) == ADMIN_CHAT_ID:
        args = context.args
        if len(args) < 1:
            await update.message.reply_text('Использование: /block <user_id>')
            return
        user_id = args[0]
        if user_id not in blocked_users:
            blocked_users.append(user_id)
        await update.message.reply_text(f'Пользователь {user_id} заблокирован.')
    else:
        await update.message.reply_text('Эта команда доступна только администратору.')

# Обработка команды /unblock
async def unblock(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if str(update.message.chat_id) == ADMIN_CHAT_ID:
        args = context.args
        if len(args) < 1:
            await update.message.reply_text('Использование: /unblock <user_id>')
            return
        user_id = args[0]
        if user_id in blocked_users:
            blocked_users.remove(user_id)
        await update.message.reply_text(f'Пользователь {user_id} разблокирован.')
    else:
        await update.message.reply_text('Эта команда доступна только администратору.')

# Обработка команды /blocked_users
async def blocked_users_list(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.message.chat_id if update.message else update.callback_query.message.chat_id
    if str(chat_id) == ADMIN_CHAT_ID:
        if not blocked_users:
            await update.effective_message.reply_text('Список заблокированных пользователей пуст.')
        else:
            await update.effective_message.reply_text('Заблокированные пользователи:\n' + '\n'.join(blocked_users))
    else:
        await update.effective_message.reply_text('Эта команда доступна только администратору.')

# Обработка нажатий на инлайн-кнопки
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    data = query.data
    if data == 'view_blocked':
        await blocked_users_list(update, context)

# HTTP сервер для поддержания активности
async def keep_alive(request):
    return web.Response(text="I'm alive!")

async def main():
    app = web.Application()
    app.router.add_get('/', keep_alive)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 8080)
    await site.start()

    application = Application.builder().token("7380668831:AAEuXyf6t44hwDEm8H4BIDeoA5h3nX1lD7A").build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    application.add_handler(MessageHandler(filters.VIDEO, handle_video))
    application.add_handler(MessageHandler(filters.Document.ALL, handle_document))
    application.add_handler(CommandHandler("reply", reply))
    application.add_handler(CommandHandler("block", block))
    application.add_handler(CommandHandler("unblock", unblock))
    application.add_handler(CommandHandler("blocked_users", blocked_users_list))
    application.add_handler(CallbackQueryHandler(button))

    await application.initialize()
    await application.start()
    await application.updater.start_polling()

    print("Бот запущен и HTTP сервер запущен на порту 8080")
    await asyncio.Event().wait()

if __name__ == '__main__':
    asyncio.run(main())