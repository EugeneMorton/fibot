"""Copyright 2018 Eugene Litvin & Alexey Lozovoy

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License."""

import datetime
import logging
from re import search

import telegram.ext

from config import token  # single-string file with my bot`s token
from schedule import (admins_gen, is_admin, adm_add)

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


def start(bot, update):
    bot.send_message(chat_id=update.message.chat_id,
                     text='Hi! I`m FIbot.')


def adm(bot, update, args):
    if not args:
        bot.send_message(chat_id=update.message.chat_id, parse_mode='Markdown', text=admins_gen(update.message.chat_id))
    elif args[0] == 'add' and is_admin(update.effective_message.from_user.id, update.message.chat.id) == 'Admin':
        reply = update.message.reply_to_message.from_user
        if update.message.reply_to_message:
            if args[1] in ['Admin', 'Moderator'] and not is_admin(chatid=update.message.chat_id, userid=reply.id):
                adm_add([update.message.chat_id, reply.id, args[1],
                         reply.first_name + ' ' + reply.last_name, '@' + reply.username])
                bot.send_message(chat_id=update.message.chat_id,
                                 text="User {0} was promoted to {1}".format(
                                     reply.first_name + ' ' + reply.last_name, args[1]))
            else:
                bot.send_message(chat_id=update.message.chat_id, text="Invalid role or user alredy admin or moderator")
        else:
            bot.send_message(chat_id=update.message.chat_id, text="reply to user you want to promote")


# TODO: Normal help message for admin/moderator
def helper(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text="Hi! I`m FIbot")


# noinspection Annotator,PyUnboundLocalVariable,PyUnboundLocalVariable,PyUnboundLocalVariable
def mute(bot, update, args, job_queue):
    muter_role = is_admin(update.effective_message.from_user.id, update.message.chat.id)
    if not muter_role:
        bot.send_message(chat_id=update.message.chat_id, text="Permission denied")
    elif not update.message.reply_to_message:
        bot.send_message(chat_id=update.message.chat_id, text="Reply person you want to mute")
    elif args and is_admin(update.message.reply_to_message.from_user.id, update.message.chat.id) != 'Admin':
        date = search(r' (\d+[d|h|m]) ', ' ' + ' '.join(args) + ' ')
        reply = update.message.reply_to_message.from_user
        if (args[0] == 'forever' and muter_role == 'Admin') or date:
            bot.restrictChatMember(chat_id=update.message.chat.id,
                                   user_id=reply.id)
            bot.send_message(chat_id=update.message.chat_id,
                             text="User {0} was muted for {1}".format(reply.first_name + ' ' + reply.last_name,
                                                                      ' '.join(args)))
            if args[0] != 'forever':
                for i in date.groups():
                    if i[-1] == 'd':
                        day = i[:-1]
                    elif i[-1] == 'h':
                        hour = i[:-1]
                    elif i[-1] == 'm':
                        minutes = i[:-1]
                job_queue.run_once(unmute_job, datetime.timedelta(days=int(day), hours=int(hour), minutes=int(minutes)),
                                   name=reply.id + update.message.chat_id,
                                   context=dict(chatid=update.message.chat_id,
                                                userid=reply.id,
                                                username=reply.first_name + ' ' + reply.last_name))


def unmute(bot, update, job_queue):
    muter_role = is_admin(update.effective_message.from_user.id, update.message.chat.id)
    if not muter_role:
        bot.send_message(chat_id=update.message.chat_id, text="Permission denied")
    elif not update.message.reply_to_message:
        bot.send_message(chat_id=update.message.chat_id, text="Reply person you want to unmute")
    else:
        reply = update.message.reply_to_message.from_user
        for job in job_queue.get_jobs_by_name(reply.id + update.message.chat_id):
            job.schedule_removal()
        job_queue.run_once(unmute_job, datetime.timedelta(),
                           name=reply.id + update.message.chat_id,
                           context=dict(chatid=update.message.chat_id,
                                        userid=reply.id,
                                        username=reply.first_name + ' ' + reply.last_name))


def unmute_job(bot, job):
    bot.restrictChatMember(chat_id=job.context['chatid'],
                           user_id=job.context['userid'],
                           can_send_messages=True, can_send_media_messages=True, can_send_other_messages=True,
                           can_add_web_page_previews=True)
    bot.send_message(chat_id=job.context['chatid'],
                     text="User {0} was unmuted".format(job.context['username']))


def main():
    ud = telegram.ext.Updater(token=token)
    dp = ud.dispatcher
    dp.add_handler(telegram.ext.CommandHandler('start', start))
    dp.add_handler(telegram.ext.CommandHandler('adm', adm, pass_args=True))
    dp.add_handler(telegram.ext.CommandHandler('help', helper))
    dp.add_handler(telegram.ext.CommandHandler('mute', mute, pass_args=True, pass_job_queue=True))
    dp.add_handler(telegram.ext.CommandHandler('unmute', unmute, pass_job_queue=True))
    ud.start_polling()
    ud.idle()


if __name__ == '__main__':
    main()
