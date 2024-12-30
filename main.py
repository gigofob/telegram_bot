import asyncio
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters, CallbackContext, CallbackQueryHandler, CommandHandler
from telegram.constants import ParseMode

# Настройте логирование
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Замените на ваш токен
BOT_TOKEN = "Вставь свой токен бота"
# ID вашего новостного канала (числовой ID или @username)
CHANNEL_ID = "@логин канала"  # Или числовой ID


# Текст подписи
SIGNATURE = "[👉 Водяной знак поста](t.me/логин канала)"

async def handle_news(update: Update, context: CallbackContext):
    user = update.effective_user
    message = update.message
    chat_id = update.effective_chat.id

    if message.photo or message.video:
        caption = message.caption or ""
        await message.reply_text("Ваша новость получена. Ожидайте подтверждения.")

        keyboard = [
            [InlineKeyboardButton("Принять", callback_data=f"accept:{message.message_id}:{chat_id}"),
             InlineKeyboardButton("Отклонить", callback_data=f"reject:{message.message_id}:{chat_id}")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await context.bot.send_message(
            chat_id=context.bot.id,  # Отправляем сообщение администратору
            text=f"Новая новость от пользователя {user.name}:\n{caption}\n\nMessage ID: {message.message_id}", #Added message ID for easier identification
            reply_markup=reply_markup,
            reply_to_message_id=message.message_id
        )
    else:
        await message.reply_text("Пожалуйста, отправьте новость с фото или видео.")

async def button_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    data = query.data.split(":")
    action = data[0]
    message_id = int(data[1])
    chat_id = int(data[2])

    if action == "accept":
        try:
            original_message = await context.bot.get_message(message_id)
            caption = original_message.caption or ""
            caption += f"\n\n{SIGNATURE}"

            if original_message.photo:
                await context.bot.send_photo(chat_id=CHANNEL_ID, photo=original_message.photo[-1].file_id, caption=caption, parse_mode=ParseMode.MARKDOWN_V2)
            elif original_message.video:
                await context.bot.send_video(chat_id=CHANNEL_ID, video=original_message.video.file_id, caption=caption, parse_mode=ParseMode.MARKDOWN_V2)
            await query.answer("Новость опубликована!")
        except Exception as e:
            await query.answer(f"Ошибка при публикации: {e}")
    elif action == "reject":
        await query.answer("Новость отклонена.")

    await query.delete_message()

async def start(update: Update, context: CallbackContext):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Отправьте новость с фото или видео!")


async def main():
    loop = asyncio.get_event_loop()
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    application.add_handler(MessageHandler(filters.PHOTO | filters.VIDEO & ~filters.COMMAND, handle_news))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(CommandHandler("start", start))
    await application.run_polling()
    logging.info("Бот запущен.")

    loop.run_forever()

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())