import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Получаем данные из Environment Variables
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
PRIVATE_GROUP_LINK = os.getenv("PRIVATE_GROUP_LINK", "https://t.me/твоя_группа")

if not TELEGRAM_TOKEN:
    logger.error("TELEGRAM_TOKEN не установлен!")
    exit(1)

# Состояния
WAITING_FOR_TELEGRAM = 1
WAITING_FOR_CLASS = 2

user_data_storage = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Запуск бота"""
    user_id = update.effective_user.id
    user_data_storage[user_id] = {}
    
    await update.message.reply_text(
        "👋 Привет! Спасибо, что записалась на пробное занятие!\n\n"
        "Чтобы я мог подготовиться, ответь на 2 вопроса:\n\n"
        "1️⃣ Напиши свой **ТГ username** (например: @nikita или просто nikita)"
    )
    return WAITING_FOR_TELEGRAM

async def get_telegram(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Получение ТГ username"""
    user_id = update.effective_user.id
    telegram_username = update.message.text.strip()
    
    if telegram_username.startswith('@'):
        telegram_username = telegram_username[1:]
    
    user_data_storage[user_id]['telegram'] = telegram_username
    
    await update.message.reply_text(
        "2️⃣ В каком классе? (9, 10 или 11)"
    )
    return WAITING_FOR_CLASS

async def get_class(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Получение класса"""
    user_id = update.effective_user.id
    class_number = update.message.text.strip()
    
    user_data_storage[user_id]['class'] = class_number
    
    # Логирование в консоль
    logger.info(f"✅ Новый ученик: @{user_data_storage[user_id]['telegram']}, класс {class_number}")
    
    final_message = (
        f"✅ Спасибо, @{user_data_storage[user_id]['telegram']}! 🎉\n\n"
        f"Я подготовился к встрече!\n\n"
        f"👇 Вот приватная группа подготовки:\n\n"
        f"{PRIVATE_GROUP_LINK}\n\n"
        f"📌 Подпишись и начни читать полезные материалы.\n\n"
        f"❓ Если есть вопросы: @nikita_prepod"
    )
    
    await update.message.reply_text(final_message)
    
    del user_data_storage[user_id]
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отмена"""
    await update.message.reply_text("Отменено. /start чтобы начать заново.")
    return ConversationHandler.END

def main():
    """Запуск бота"""
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            WAITING_FOR_TELEGRAM: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_telegram)],
            WAITING_FOR_CLASS: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_class)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )
    
    app.add_handler(conv_handler)
    
    logger.info("🤖 Бот запущен!")
    app.run_polling()

if __name__ == '__main__':
    main()
