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
from classes.team_base import TeamBase

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


# TODO: combine common logic for add_team and remove_team into one method
async def add_team(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not context.args:
        await update.message.reply_text(
            "Team_id parameter is required. Usage: /add_team <team_id>"
        )
        return

    chat_id = update.message.chat_id
    club = chat_registry.get_club_by_chat_id(chat_id)
    if not club:
        await update.message.reply_text(
            f"The club with id #{chat_id} does not exist, please register it first by using /start command"
        )
        return

    # TODO: for now TeamBase is used
    # TODO: get Team name from the system (and move this logic to the TeamBase class, if needed)
    if club.add_team(
        TeamBase(
            context.args[0],
            update.message.message_thread_id,
            f"Team {update.message.message_thread_id}",
        )
    ):
        chat_registry.store_club(club)
        await update.message.reply_text(
            f"Team with id {context.args[0]} has been added to the club with chat_id: {chat_id}"
        )
        return

    # TODO: move message sending to the club when the ChatHelper is implemented
    await update.message.reply_text(
        f"Team with id {context.args[0]} already exists in the club with chat_id: {chat_id}"
    )


async def remove_team(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not context.args:
        await update.message.reply_text(
            "The team_id argument is required. Usage: /remove_team <team_id>"
        )
        return

    chat_id = update.message.chat_id
    club = chat_registry.get_club_by_chat_id(chat_id)
    if not club:
        await update.message.reply_text(
            f"The club with id #{chat_id} does not exist, please register it first by using /start command"
        )
        return

    if club.remove_team(context.args[0]):
        chat_registry.store_club(club)
        await update.message.reply_text(
            f"Team with id {context.args[0]} has been removed from the club with chat_id: {chat_id}"
        )
        return

    await update.message.reply_text(
        f"Team with id {context.args[0]} does not exist in the club with chat_id: {chat_id}"
    )


async def help(update, context):
    # TODO add info where user can find team_id
    help_message = """
    Available commands:
    /help - Display available commands and their descriptions
    /start - Start the bot + register the club
    /run_club_polling - Run polling for the club
    /stop_club_polling - Stop polling for the club
    /add_team <team_id> - Use the /add_team <team_id> command to register a new team within general chat or topic. This command binds the newly created team to the context from which the command is invoked, ensuring all related notifications and events are directed appropriately.. 
    /remove_team <team_id> - Remove team with specific team_id to the club. May be invoked within general chat or topic.
    """
    # TODO: should the following line be replaced with ChatHelper instance method?
    await context.bot.send_message(chat_id=update.message.chat_id, text=help_message)


if __name__ == "__main__":
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    chat_registry.add_app_instance(application)

    application.add_handler(CommandHandler("help", help))
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("add_team", add_team))
    application.add_handler(CommandHandler("remove_team", remove_team))
    application.add_handler(CommandHandler("run_club_polling", run_club_polling))
    application.add_handler(CommandHandler("stop_club_polling", stop_club_polling))
    application.add_handler(MessageHandler(filters.COMMAND, help))

    application.run_polling()
