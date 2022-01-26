import logging
from requests import HTTPError
from telegram import Update, ForceReply
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from pythonpancakes import PancakeSwapAPI
ps = PancakeSwapAPI()
# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
from database_operations import *

logger = logging.getLogger(__name__)

updater = Updater("your-api-key")






















# Define a few command handlers. These usually take the two arguments update and
# context.
def start(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    update.message.reply_markdown_v2(
        fr'Hi {user.mention_markdown_v2()}\!',
        reply_markup=ForceReply(selective=True),
    )

def bscCheckContractValid(contract_addr):
    """Echo the user message."""
    try:
        token = ps.tokens(contract_addr)
        return True, token["data"]["name"]
    except (HTTPError, ValueError) as e:
        if "invalid address" in str(e):
            return False,"invalid address"
        elif "Not Found" in str(e):
            return False,"Not found"
        elif "is not in a valid format" in str(e):
            return False,"invalid format for address"
        else:
            return False, "unknown error"


def help_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    update.message.reply_text('Help!')


def echo(update: Update, context: CallbackContext) -> None:
    """Echo the user message."""
    update.message.reply_text("Unknown command, check available commands via /help")

def setContractBSC(update: Update, context: CallbackContext) -> None:
    ret_val = bscCheckContractValid(context.args[0])
    if ret_val[0]:
        update.message.reply_text("Binance contract for {" + ret_val[1] + "} ,saved!")
        saveUserContractAddress(update.message.chat_id, context.args[0], 0)
        saveUserAlarmState(update.message.chat_id, 1)
    else:
        update.message.reply_text("Error! " + ret_val[1])



def startNotifications(update: Update, context: CallbackContext) -> None:
    chat_id = update.message.chat_id


    user_info = checkAccountInfo("SELECT timer FROM accounts WHERE username = " + "'" + str(chat_id) + "';")
    print(user_info )

    job_removed = remove_job_if_exists(str(chat_id), context)

    updater.job_queue.run_repeating(actionUserPriceNotification,
                                        int(user_info[0][0]), context= chat_id, name=str(chat_id))

    saveUserAlarmState(chat_id, 1)
    if job_removed:
        update.message.reply_text("Old job removed, Notifications are enabled!")
    else:
        update.message.reply_text("Notifications are enabled!")

def stopNotifications(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    """Add a job to the queue."""
    chat_id = update.message.chat_id
    try:
        job_removed = remove_job_if_exists(str(chat_id), context)
        saveUserAlarmState(chat_id, 0)
        if job_removed:
            update.message.reply_text("Notifications are disabled!")
        else:
            update.message.reply_text("ERROR 1")
    except (IndexError, ValueError):
        update.message.reply_text('Usage: /set <seconds>')




def setLicense(update: Update, context: CallbackContext) -> None:
    """Echo the user message."""
    update.message.reply_text("Notifications are disabled!")

def setShowType(update: Update, context: CallbackContext) -> None:
    """Echo the user message."""
    update.message.reply_text("Notifications are disabled!")

def setInterval(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    """Add a job to the queue."""
    chat_id = update.message.chat_id
    try:
        # args[0] should contain the time for the timer in seconds
        due = int(context.args[0])
        if due < 0:
            update.message.reply_text('Sorry we can not go back to future!')
            return

        job_removed = remove_job_if_exists(str(chat_id), context)
        context.job_queue.run_repeating(actionUserPriceNotification, due, context=chat_id, name=str(chat_id))

        text = 'Timer successfully set!'
        if job_removed:
            text += ' Old one was removed.'
        update.message.reply_text(text)
        saveUserTimerInterval(chat_id, context.args[0])
    except (IndexError, ValueError):
        update.message.reply_text('Usage: /set <seconds>')

def setAmount(update: Update, context: CallbackContext) -> None:
    chat_id = update.message.chat_id
    try:
        due = int(context.args[0])
        if due <= 0:
            update.message.reply_text('Error, Amount can not be zero')
            return
        saveUserAmount(chat_id, context.args[0])
        text = 'Amount {' + str(context.args[0]) + '}Saved'
        update.message.reply_text(text)
    except (IndexError, ValueError):
        update.message.reply_text('Usage: /set <seconds>')



# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.
# Best practice would be to replace context with an underscore,
# since context is an unused local variable.
# This being an example and not having context present confusing beginners,
# we decided to have it present as context.
def start(update: Update, context: CallbackContext) -> None:
    """Sends explanation on how to use the bot."""
    update.message.reply_text('Hi! Use /set <seconds> to set a timer')


def actionUserPriceNotification(context: CallbackContext) -> None:
    job = context.job
    user_info = checkAccountInfo("SELECT contract, amount FROM accounts WHERE username = " + "'" + str(job.context) + "';")
    token = ps.tokens(user_info[0][0])
    current_price = float(token["data"]["price"])
    current_price = "%.8f" % round(current_price, 8)
    if int(user_info[0][1]) > 0:
        balance = float(current_price)*float(user_info[0][1])
        balance = "%.2f" % round( balance, 2)
        response = token["data"]["name"].lower() + ", $" + current_price+ ", $" + str(balance)
    else:
        response = token["data"]["name"].lower() + ", $" + current_price
    context.bot.send_message(job.context, text = response)


def remove_job_if_exists(name: str, context: CallbackContext) -> bool:
    """Remove job with given name. Returns whether job was removed."""
    current_jobs = context.job_queue.get_jobs_by_name(name)
    if not current_jobs:
        return False
    for job in current_jobs:
        job.schedule_removal()
    return True






def unset(update: Update, context: CallbackContext) -> None:
    """Remove the job if the user changed their mind."""
    chat_id = update.message.chat_id
    job_removed = remove_job_if_exists(str(chat_id), context)
    text = 'Timer successfully cancelled!' if job_removed else 'You have no active timer.'
    update.message.reply_text(text)

def connect():
    try:
        user_list = checkAccountInfo("select username, timer, active from accounts")

        if user_list is None:
             return
        else:
            count = 0
            for i in user_list:
                try:
                    if int(user_list[count][2]) == 1:
                        timer_val = 0;
                        if user_list[count][1] is not None:
                            timer_val = int(user_list[count][1])
                        else:
                            timer_val = 60;
                        updater.job_queue.run_repeating(actionUserPriceNotification,
                                                    timer_val, context=user_list[count][0],
                                                    name=str(user_list[count][0]))
                except Exception as error:
                    print(error)

                count = count + 1

    except Exception as error:
        print(error)
    finally:
            print('Database connection closed.')

def main() -> None:
    """Start the bot."""
    # Create the Updater and pass it your bot's token.

    connect()


    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # on different commands - answer in Telegram
    dispatcher.add_handler(CommandHandler("start", startNotifications))
    dispatcher.add_handler(CommandHandler("stop", stopNotifications))
    dispatcher.add_handler(CommandHandler("setamount", setAmount))
    dispatcher.add_handler(CommandHandler("setinterval", setInterval))
    dispatcher.add_handler(CommandHandler("setcontractBSC", setContractBSC))


    # on non command i.e message - echo the message on Telegram
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
