# -*- coding: utf-8 -*-

# Bots logic

"""Simple Bot to send timed Telegram messages.
# This program is dedicated to the public domain under the CC0 license.
This Bot uses the Updater class to handle the bot and the JobQueue to send
timed messages.
First, a few handler functions are defined. Then, those functions are passed to
the Dispatcher and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.
Usage:
Basic Alarm Bot example, sends a message after a set time.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""

from telegram.ext import Updater, CommandHandler, CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import logging
from config import *
from consts import *
import s9api


# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
# Setup individual logger for this module
logger = logging.getLogger(__name__)

# Main func for run bot
def main():
    """Run bot"""

    # Prepare connection
    REQUEST_KWARGS = {
        'proxy_url': proxy_url, # 'socks5://ip:port'
        # Optional, if you need authentication:
        'urllib3_proxy_kwargs': {
            'username': proxy_username,
            'password': proxy_password,
        }
    }
    # Get the Updater by TOKEN and proxy
    updater = Updater(token, request_kwargs=REQUEST_KWARGS)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # Register commands handler
    dp.add_handler(CommandHandler("start", onStart))
    dp.add_handler(CommandHandler("next", onNext))
    # Register callback handler for buttons
    dp.add_handler(CallbackQueryHandler(onButtonClick))

    # Setup log all errors
    dp.add_error_handler(onError)

    # Start the Bot
    updater.start_polling()

    # Block until you press Ctrl-C or the process receives SIGINT, SIGTERM or
    # SIGABRT. This should be used most of the time, since start_polling() is
    # non-blocking and will stop the bot gracefully.
    updater.idle()

# Validate users
def isValidUser(update):
    return update.message.from_user.username in USERS

# Define a few command handlers. These usually take the two arguments bot and
# update. Error handlers also receive the raised TelegramError object in error.
def onStart(bot, update):
    # Filter users
    if not isValidUser(update):
        update.message.reply_text(NOT_VALID_USR_MESSAGE)
        return

    # Hello
    update.message.reply_text(START_COMMAND_MESSAGE)

# show buttons
def onNext(bot, update):
    # Filter users
    if not isValidUser(update):
        return

    # готовим клавиатуру
    keyboard = [[InlineKeyboardButton("📋 Состояние", callback_data=QUESTION_INFO),
                 InlineKeyboardButton("⚖ Статистика", callback_data=QUESTION_STAT)]]
    # готовим разметку
    reply_markup = InlineKeyboardMarkup(keyboard)
    # выводим текст с разметкой
    update.message.reply_text('Чего изволите?', reply_markup=reply_markup)

# onButtonClick
def onButtonClick(bot, update):
    query = update.callback_query
    # answer
    bot.edit_message_text(text=getAnswerText(query.data),
                          chat_id=query.message.chat_id,
                          message_id=query.message.message_id)

# errorHandler
def onError(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)

# Create answer
def getAnswerText(question):
    if question == QUESTION_INFO:
        return s9api.getAboutMiners() + "\n\n" + NEXT
    elif question == QUESTION_STAT:
        return s9api.getAboutMiners() + "\n\n" + NEXT

if __name__ == '__main__':
    main()
