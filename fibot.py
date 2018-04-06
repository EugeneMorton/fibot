from schedule import (schedule_gen, button_gen, admins_gen, isAdmin, admAdd)
import datetime
import telegram.ext
import logging
from re import match

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
keyboard = button_gen()


def start(bot, update):
    bot.send_message(chat_id=update.message.chat_id,
                     text='Hi! I`m FIbot. I`ll send you your schedule, homework and other useful info')


def adm(bot, update, args):
    if not args:
        bot.send_message(chat_id=update.message.chat_id, text=admins_gen(update.message.chat_id))
    elif args[0] == 'add' and isAdmin(update.effective_message.from_user.id, update.message.chat.id) == 'Admin':
        reply = update.message.reply_to_message.from_user
        if update.message.reply_to_message:
            if args[1] in ['Admin', 'Moderator'] and not isAdmin(chatid=update.message.chat_id, userid=reply.id):
                admAdd([update.message.chat_id, reply.id, args[1], reply.first_name + ' ' + reply.last_name])
                bot.send_message(chat_id=update.message.chat_id,
                                 text="User {0} was promoted to {1}".format(
                                     reply.first_name + ' ' + reply.last_name, args[1]))
            else:
                bot.send_message(chat_id=update.message.chat_id, text="Invalid role or user alredy admin or moderator")

def keyboard_job(bot, job):
    globals()['keyboard'] = button_gen()
    logger.debug('Updated keyboard')


def schedule(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text=schedule_gen(),
                     reply_markup=telegram.InlineKeyboardMarkup(keyboard))


def helper(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text="Hi! I`m FIbot\nI can show you your schedule - use:\n"
                                                          "/schedule (now | tom | DD-MM-YYYY) \nAlso i have "
                                                          "some undocumented features :D\nMy developer is working on "
                                                          "adding your homework to my database. He`s nice :3")


def button(bot, update):
    query = update.callback_query
    if match(r'\d{2}-\d{2}-\d{4}', query.data):
        bot.edit_message_text(text=schedule_gen([query.data]),
                              chat_id=query.message.chat.id,
                              message_id=query.message.message_id,
                              reply_markup=telegram.InlineKeyboardMarkup(button_gen()))


def mute(bot, update, args, job_queue):
    reply = update.message.reply_to_message.from_user
    muter_role = isAdmin(update.effective_message.from_user.id, update.message.chat.id)
    if muter_role in ['Moderator', 'Admin'] and not isAdmin(reply.id, update.message.chat.id) == 'Admin':
        if not update.message.reply_to_message:
            bot.send_message(chat_id=update.message.chat_id, text="Reply person you want to mute")
        elif args and (match(r'\d{1,3}', args[0]) or (args[0] == 'forever' and muter_role == 'Admin')):
            bot.restrictChatMember(chat_id=update.message.chat.id,
                                   user_id=reply.id)
            if args[0] == 'forever' or int(args[0]) != 0:
                bot.send_message(chat_id=update.message.chat_id,
                                 text="User {0} was muted for {1} minutes".format(
                                     reply.first_name + ' ' + reply.last_name, args[0]))
            else:
                for job in job_queue.get_jobs_by_name(reply.id+update.message.chat_id):
                    job.schedule_removal()

            if args[0] != 'forever':
                job_queue.run_once(unmute_job, datetime.timedelta(minutes=int(args[0])),
                                   name=reply.id + update.message.chat_id,
                                   context=dict(chatid=update.message.chat_id,
                                                userid=reply.id,
                                                username=reply.first_name + ' ' + reply.last_name))
        else:
            bot.send_message(chat_id=update.message.chat_id, text="Specify time in minutes")
    else:
        bot.send_message(chat_id=update.message.chat_id, text="Permission denied")


def unmute_job(bot, job):
    bot.restrictChatMember(chat_id=job.context['chatid'],
                           user_id=job.context['userid'],
                           can_send_messages=True, can_send_media_messages=True, can_send_other_messages=True,
                           can_add_web_page_previews=True)
    bot.send_message(chat_id=job.context['chatid'],
                     text="User {0} was unmuted".format(job.context['username']))


def main():
    ud = telegram.ext.Updater(token='')
    dp = ud.dispatcher
    jq = ud.job_queue
    dp.add_handler(telegram.ext.CommandHandler('start', start))
    dp.add_handler(telegram.ext.CommandHandler('adm', adm, pass_args=True))
    dp.add_handler(telegram.ext.CommandHandler('schedule', schedule))
    dp.add_handler(telegram.ext.CommandHandler('help', helper))
    dp.add_handler(telegram.ext.CommandHandler('mute', mute, pass_args=True, pass_job_queue=True))
    dp.add_handler(telegram.ext.CallbackQueryHandler(button))
    jq.run_repeating(keyboard_job, datetime.timedelta(days=1),
                     datetime.datetime.now().replace(hour=00, minute=0) + datetime.timedelta(days=1))
    ud.start_polling()
    ud.idle()


if __name__ == '__main__':
    main()