import logging
from telegram import Update, Poll
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, Updater, CallbackContext


# setting up logging module https://github.com/python-telegram-bot/python-telegram-bot/wiki/Exceptions%2C-Warnings-and-Logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

#  retrieves a logger named after the current module from the logging module's hierarchy of loggers
logger = logging.getLogger(__name__)

TOKEN = ''

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="I'm a bot, please talk to me!")

if __name__ == '__main__':
    application = ApplicationBuilder().token(TOKEN).build()
    
    start_handler = CommandHandler('poll', start)
    application.add_handler(start_handler)
    
    application.run_polling()