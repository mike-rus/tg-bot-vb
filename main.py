import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, filters, MessageHandler


# setting up logging module https://github.com/python-telegram-bot/python-telegram-bot/wiki/Exceptions%2C-Warnings-and-Logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

#  retrieves a logger named after the current module from the logging module's hierarchy of loggers
logger = logging.getLogger(__name__)

TOKEN = ''

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await context.bot.send_message(chat_id=update.effective_chat.id, text="I'm a bot, please talk to me!")

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="глупость")

async def create_poll(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # """Creates and pins a poll based on some condition."""
    # Here you can define your condition
    # await context.bot.send_message(chat_id=update.effective_chat.id, text="Нахер идите, сами создавайте опросы!")
    condition_met = True

    if condition_met:
        questions = ["Yes", "Definetly", "There is no other choice then yes"]  # Add your options here
        message = await context.bot.send_poll(
            update.effective_chat.id,
            "Should we do it?",  # Your poll title here
            questions,
            allows_multiple_answers=False,
            is_anonymous=False,
        )
        # Pinning the poll
        await context.bot.pin_chat_message(
            chat_id=update.effective_chat.id,
            message_id=message.message_id,
        )

# TODO: is this needed
    # Save some info about the poll the bot_data for later use in receive_poll_answer
    payload = {
        message.poll.id: {
            "questions": questions,
            "message_id": message.message_id,
            "chat_id": update.effective_chat.id,
            "answers": 0,
        }
    }
    context.bot_data.update(payload)
        
# def error(update: Update, context: CallbackContext) -> None:
#     """Logs errors caused by updates."""
#     logger.warning('Update "%s" caused error "%s"', update, context.error)

def main() -> None:    
    application = ApplicationBuilder().token(TOKEN).build()
    
    start_handler = CommandHandler('start', start)

    echo_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), echo)
    # application.add_handler(echo_handler)

    poll_handler = CommandHandler('create_poll', create_poll)
    application.add_handler(start_handler)
    application.add_handler(poll_handler)
    # application.add_handler(error)
    
    application.run_polling()

if __name__ == '__main__':
    main()