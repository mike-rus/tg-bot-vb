import os
import logging
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    filters,
    ContextTypes,
    CommandHandler,
    MessageHandler,
)

from classes.chat_registry import ChatRegistry
from classes.club import Club

REGISTRY_FOLDER = f"{os.getcwd()}/registry"

chat_registry = ChatRegistry(REGISTRY_FOLDER)


# setting up logging module https://github.com/python-telegram-bot/python-telegram-bot/wiki/Exceptions%2C-Warnings-and-Logging
logging.basicConfig(
    # filename='bot.log',   #TODO add log rotating
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.ERROR,
)

#  retrieves a logger named after the current module from the logging module's hierarchy of loggers
logger = logging.getLogger(__name__)

BOT_TOKEN = os.environ.get("BOT_TOKEN")


# Perhaps not required, can be used as template for team_polling
async def run_club_polling(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Runs polling for the club associated with the chat_id.
    """
    await chat_registry.run_polling(update.message.chat_id)
    await chat_registry.delete_message_delayed(
        update.message.chat_id, update.message.message_id, delay=10
    )


# Perhaps not required, can be used as template for team_polling
# I think it's required to move or guess better add scheduled polling to the team from the club so that there's the option to disable it for certain topics(teams).
async def stop_club_polling(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Stops polling for the club associated with the chat_id.
    """
    await chat_registry.stop_polling(update.message.chat_id)
    await chat_registry.delete_message_delayed(
        update.message.chat_id, update.message.message_id, delay=10
    )


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Initiates the start of the bot.
    Adds the club to the registry.
    """
    await chat_registry.add_club(
        Club(update.message.chat_id, update.effective_chat.title)
    )
    await chat_registry.delete_message_delayed(
        update.message.chat_id, update.message.message_id, delay=10
    )


async def add_team(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    pass


async def help(update, context):
    help_message = """
    Available commands:
    /help - Display available commands and their descriptions
    /start - Start the bot + register the club
    /run_club_polling - Run polling for the club
    /stop_club_polling - Stop polling for the club
    /add_team - We should recognise message_thread_id of the topic as it unique ID for general 0. Same chat_id for all topics. I haven't investigated it deeply. In any case, we need to attach team to the club (with oportunity to send msgs to specific topic), initialize it with a title, team_id, topic_id
    """
    await context.bot.send_message(chat_id=update.message.chat_id, text=help_message)


if __name__ == "__main__":
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    chat_registry.add_app_instance(application)

    application.add_handler(CommandHandler("help", help))
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("add_team", add_team))
    application.add_handler(CommandHandler("run_club_polling", run_club_polling))
    application.add_handler(CommandHandler("stop_club_polling", stop_club_polling))
    application.add_handler(MessageHandler(filters.COMMAND, help))

    application.run_polling()
