#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
"""
This bot was made by e-caste in 2020 to help Computer Networks students to prepare for the exam.
Good luck!
"""
# NOTE: this script does not contain fstrings to allow compatibility with Python 3.5

from telegram import Bot, ReplyKeyboardMarkup
from telegram.parsemode import ParseMode
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters,
                          ConversationHandler, PicklePersistence, messagequeue as mq, JobQueue)
from telegram.utils.helpers import mention_html
from telegram.utils.request import Request
import logging
from math import ceil
import os
import sys
import traceback
from datetime import time, datetime, timedelta
import shutil
from string import whitespace
from contextlib import suppress
import json

HTML = ParseMode.HTML
debug = sys.platform.startswith("darwin")

if debug:
    from secret import token, castes_chat_id, link, usage_history_file
    os.environ['LINK'] = link
else:
    # import Docker environment variables
    token = os.environ["TOKEN"]
    castes_chat_id = os.environ["CST_CID"]
    usage_history_file = os.environ["USAGE_FILE"]

# import from quiz after setting environment variables
from quiz import (get_number_of_questions, extract_questions, get_q_n_a, file_name, get_available_answers,
                  download_latest_google_doc, set_forbidden_questions, clean_comments_from_text)

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

CHOOSING_NQ, CHANGE_NQ, QUIZ = range(3)

text = ""

__change_number_button = 'Set number of questions'
__quick_quiz_number_button = 'Quick quiz - 5'
__exam_sim_covid19_number_button = 'Exam simulation - 31'
__exam_sim_number_button = 'Exam simulation - 28'
__cancel_button = "Cancel"

reply_keyboard_questions = [[__change_number_button],
                            [__quick_quiz_number_button],
                            [__exam_sim_covid19_number_button],
                            [__exam_sim_number_button],
                            [__cancel_button]]
questions_markup = ReplyKeyboardMarkup(reply_keyboard_questions, one_time_keyboard=True)

reply_keyboard_a = [['A', 'Skip'],
                    [__cancel_button]]
reply_keyboard_ab = [['A', 'B'],
                     ['Skip', __cancel_button]]
reply_keyboard_abc = [['A', 'B'],
                      ['C', 'Skip'],
                      [__cancel_button]]
reply_keyboard_abcd = [['A', 'B'],
                       ['C', 'D'],
                       ['Skip', __cancel_button]]
reply_keyboard_abcde = [['A', 'B'],
                        ['C', 'D'],
                        ['E', 'Skip'],
                        [__cancel_button]]
reply_keyboard_abcdef = [['A', 'B'],
                         ['C', 'D'],
                         ['E', 'F'],
                         ['Skip', __cancel_button]]
markup_a = ReplyKeyboardMarkup(reply_keyboard_a, one_time_keyboard=True)
markup_ab = ReplyKeyboardMarkup(reply_keyboard_ab, one_time_keyboard=True)
markup_abc = ReplyKeyboardMarkup(reply_keyboard_abc, one_time_keyboard=True)
markup_abcd = ReplyKeyboardMarkup(reply_keyboard_abcd, one_time_keyboard=True)
markup_abcde = ReplyKeyboardMarkup(reply_keyboard_abcde, one_time_keyboard=True)
markup_abcdef = ReplyKeyboardMarkup(reply_keyboard_abcdef, one_time_keyboard=True)


def start(update, context):
    if update:
        reply = "Hi <b>" + str(update.message.from_user.first_name) + "</b>, welcome to Networks Quiz Bot!" \
                if update and update.message else "Hi, welcome to Network Quiz Bot!"
        if update and update.message:
            update.message.reply_text(
                text=reply,
                parse_mode=HTML,
                reply_markup=questions_markup
            )
            logger.info("User " + __get_username(update) + " started a quiz.")
            return CHOOSING_NQ


def __init_usage_stats(context):
    context.bot_data['usage_stats'] = {
        'daily': set(),
        'weekly': set(),
        'monthly': set(),
        'total': set(),
    }


def reply_to_choose_nq(update, context):
    n_q_max = get_number_of_questions()
    if update and update.message:
        update.message.reply_text("Please enter a number ≤ " + str(n_q_max))
        return CHANGE_NQ  # goto choose_number_of_questions()


def choose_number_of_questions(update, context):
    if update and update.message:
        msg_text = update.message.text
        n_q_max = get_number_of_questions()
        if msg_text.isdigit():
            if 1 <= int(msg_text) <= n_q_max:
                context.user_data['n_q'] = int(msg_text)
                logger.info("User " + __get_username(update) + " selected custom number of questions: " + msg_text)
            else:
                update.message.reply_text("Number out of range. Please enter a number in the [1,"
                                          + str(n_q_max) + "] interval.")
                return CHANGE_NQ  # loop
        else:
            update.message.reply_text("Input not recognized. Please try again.")
            return CHANGE_NQ  # loop

        __prepare_user_for_quiz(context)
        quiz_question(update, context)

        return QUIZ


def set_default_number_of_questions(update, context):
    if update and update.message:
        if update and update.message.text == __quick_quiz_number_button:
            n_q = 5
        elif update and update.message.text == __exam_sim_covid19_number_button:
            n_q = 31
        else:
            n_q = 28
        context.user_data['n_q'] = n_q
        logger.info("User " + __get_username(update) + " selected default number of questions: " + str(n_q))

        __prepare_user_for_quiz(context)
        quiz_question(update, context)

        return QUIZ


def __prepare_user_for_quiz(context):
    if 'n_q' not in context.user_data:
        context.user_data['n_q'] = 0
    context.user_data['questions'] = extract_questions(context.user_data['n_q'])
    context.user_data['q_counter'] = 0
    context.user_data['current_quiz'] = {
        'correct': 0,
        'skipped': 0
    }
    if 'stats' not in context.user_data:
        context.user_data['stats'] = {
            'total': 0,
            'correct': 0,
            'wrong': 0,
            'skipped': 0,
            'marks': []
        }
        context.user_data['stats']['last_quiz'] = {
            'total': 0,
            'correct': 0,
            'wrong': 0,
            'skipped': 0,
            'mark': 0
        }


def __get_q_and_a(context):
    q, a, comment = get_q_n_a(text,
                              context.user_data['questions'][context.user_data['q_counter']])
    return q, a, comment


def __send_question(update, context):
    if update and update.message:
        q, a, comment = __get_q_and_a(context)
        avail_ans = get_available_answers(q)
        if 'B' not in avail_ans:
            markup = markup_a
        elif 'B' in avail_ans and 'C' not in avail_ans:
            markup = markup_ab
        elif 'C' in avail_ans and 'D' not in avail_ans:
            markup = markup_abc
        elif 'D' in avail_ans and 'E' not in avail_ans:
            markup = markup_abcd
        elif 'E' in avail_ans and 'F' not in avail_ans:
            markup = markup_abcde
        else:
            markup = markup_abcdef
        context.user_data['current_quiz']['ans'] = a
        context.user_data['current_quiz']['comment'] = comment
        # Quiz 58 -- 1/28
        update.message.reply_text(text="<b>Quiz " + str(context.user_data['questions'][context.user_data['q_counter']])
                                       + " -- " + str(context.user_data['q_counter'] + 1) + "/" +
                                       str(context.user_data['n_q']) + "</b>\n"
                                       + q.replace("<", "&lt;").replace(">", "&gt;").replace("&", "&amp;")  # WRAP in html formatting
                                       .replace(" A)", "<b>A)</b>").replace(" B)", "<b>B)</b>").replace(" C)", "<b>C)</b>")
                                       .replace(" D)", "<b>D)</b>").replace(" E)", "<b>E)</b>").replace(" F)", "<b>F)</b>")
                                       .replace("&lt;", "<").replace("&gt;", ">").replace("&amp;", "&"),   # UNWRAP html formatting
                                  parse_mode=HTML,
                                  reply_markup=markup)
        context.user_data['q_counter'] += 1


def __save_stats(context):
    d = context.user_data
    correct = d['current_quiz']['correct']
    skipped = d['current_quiz']['skipped']
    total = d['n_q']
    wrong = total - correct - skipped
    max_mark = 31 if context.user_data['n_q'] == 31 else 28
    mark = ceil((correct - wrong * .5) / total * max_mark)

    s = d['stats']
    s['total'] += total
    s['correct'] += correct
    s['skipped'] += skipped
    s['wrong'] += wrong
    s['marks'].append(mark)

    last = s['last_quiz']
    last['total'] = total
    last['correct'] = correct
    last['skipped'] = skipped
    last['wrong'] = wrong
    last['mark'] = mark


def __update_bot_usage(chat_id, context):
    if not context.bot_data.get('usage_stats'):
        __init_usage_stats(context)

    context.bot_data['usage_stats']['daily'].add(chat_id)
    context.bot_data['usage_stats']['weekly'].add(chat_id)
    context.bot_data['usage_stats']['monthly'].add(chat_id)
    context.bot_data['usage_stats']['total'].add(chat_id)


def __print_quiz_stats(update, context):
    if update and update.message:
        last = context.user_data['stats']['last_quiz']
        max_mark = 31 if context.user_data['n_q'] == 31 else 28
        update.message.reply_text(text="Quiz finished. Your result: <b>" + str(last['mark']) + "/30</b> (max " +
                                       str(max_mark) + ")\n"
                                       "<i>Correct: " + str(last['correct']) + " -- Wrong: " + str(last['wrong'])
                                       + " -- Not given: " + str(last['skipped']) + "</i>",
                                  parse_mode=HTML)


def __finish_quiz(update, context):
    __save_stats(context)
    __print_quiz_stats(update, context)
    __clear_temp_user_data(context)
    if update and update.message and update.message.chat_id:
        __update_bot_usage(update.message.chat_id, context)
    logger.info("User " + __get_username(update) + " finished a quiz with "
                + str(context.user_data['stats']['last_quiz']['mark']) + ".")


def quiz_question(update, context):
    if context.user_data['q_counter'] == context.user_data['n_q']:
        __finish_quiz(update, context)
        return ConversationHandler.END
    else:
        __send_question(update, context)


def quiz_ans(update, context):
    if update and update.message:
        with suppress(KeyError):
            ans = update.message.text
            qnum = str(context.user_data['questions'][context.user_data['q_counter'] - 1])
            if ans == 'Skip':
                context.user_data['current_quiz']['skipped'] += 1
                reply = "<b>Skipping...</b> The correct answer is " + context.user_data['current_quiz']['ans']
                logger.info("User " + __get_username(update) + " skipped question #" + qnum + ".")
            elif ans == context.user_data['current_quiz']['ans']:
                context.user_data['current_quiz']['correct'] += 1
                reply = "<b>Correct!</b>"
                logger.info("User " + __get_username(update) + " got question #" + qnum + " right!")
            else:
                reply = "<b>Wrong.</b> The correct answer is " + context.user_data['current_quiz']['ans']
                logger.info("User " + __get_username(update) + " got question #" + qnum + " wrong.")

            if update and update.message:
                update.message.reply_text(text=reply + "\n" + context.user_data['current_quiz']['comment']
                                          .replace("<", "&lt;").replace(">", "&gt;").replace("&", "&amp;")  # WRAP in html formatting
                                          .replace("&lt;", "<").replace("&gt;", ">").replace("&amp;", "&"),  # UNWRAP html formatting
                                          parse_mode=HTML)

                del context.user_data['current_quiz']['ans']
                del context.user_data['current_quiz']['comment']

                quiz_question(update, context)

                return QUIZ


def cancel(update, context):
    if update and update.message:
        update.message.reply_text(text="<i>Quiz canceled.</i> Come back later to try again!",
                                  parse_mode=HTML)
        logger.info("User " + __get_username(update) + " canceled.")
        __clear_temp_user_data(context)

        return ConversationHandler.END


def show_statistics(update, context):
    if 'stats' not in context.user_data:
        __prepare_user_for_quiz(context)
    s = context.user_data['stats']
    if update and update.message:
        update.message.reply_text(text="Total answered: " + str(s['total']) + "\n"
                                       "Correct answers: " + str(s['correct'])
                                       + " -- <b>" + str(round(s['correct'] / s['total'] * 100, 2)) + "%</b>\n"
                                       "Wrong answers: " + str(s['wrong'])
                                       + " -- " + str(round(s['wrong'] / s['total'] * 100, 2)) + "%\n"
                                       "Skipped answers: " + str(s['skipped'])
                                       + " -- " + str(round(s['skipped'] / s['total'] * 100, 2)) + "%\n"
                                       "\n"
                                       "Average mark: <b>" + str(round(sum(s['marks']) / len(s['marks']), 2)) + "</b>\n"
                                       "Highest mark: " + str(max(s['marks'])) + "\n"
                                       "Lowest mark: " + str(min(s['marks']))
                                        if len(s['marks']) > 0 else "No stats yet. Try your first quiz with /start!",
                                  parse_mode=HTML)
        logger.info("User " + __get_username(update) + " asked for his stats.")


def show_help(update, context):
    if update and update.message:
        update.message.reply_text(text="Use /start to begin.\n"
                                       "Use /stats to check your statistics.\n"
                                       "Use /help to show this help.")
        return ConversationHandler.END


def __clear_temp_user_data(context):
    keys_to_delete = ['current_quiz', 'n_q', 'q_counter', 'questions']
    for key in keys_to_delete:
        if key in context.user_data:
            del context.user_data[key]


def __get_username(update):
    if update and update.message:
        u = update.message.from_user.username
        u2 = update.message.from_user.first_name
        return str(u) if u else str(u2)
    return "user"


def update_quiz_file(context):
    # make backup of old file
    shutil.copy(file_name, file_name + '.bak')
    # download
    logger.info(download_latest_google_doc(use_logger=True))
    # test the new file does not give an error
    try:
        __read_text()
    except FileNotFoundError:
        # if it does, revert to backup and notify dev
        shutil.copy(file_name + '.bak', file_name)
        __read_text()
        context.bot.send_message(chat_id=castes_chat_id,
                                 text="Updated file was not found")
    if set(text) <= set(whitespace):
        shutil.copy(file_name + '.bak', file_name)
        __read_text()
        context.bot.send_message(chat_id=castes_chat_id,
                                 text="New file is empty")
    if "<!DOCTYPE html>" in text:
        shutil.copy(file_name + '.bak', file_name)
        __read_text()
        context.bot.send_message(chat_id=castes_chat_id,
                                 text="New file is HTML error")
    set_forbidden_questions()
    # otherwise, keep backup (it will be overwritten) and new file


def handle_usage_stats(context):
    if not context.bot_data.get('usage_stats'):
        __init_usage_stats(context)

    # send stats
    context.bot.send_message(chat_id=castes_chat_id,
                             text="<b>Bot's usage stats</b>:\n" + "\n".join([k + " " + str(len(v))
                                                                            for k, v in context.bot_data['usage_stats'].items()
                                                                        ]),
                             parse_mode=HTML)

    # save to file
    usage_stats_serializable = {k: list(v) for k, v in context.bot_data['usage_stats'].items()}  # convert sets to lists

    if not os.path.isfile(usage_history_file):
        if os.path.isdir(usage_history_file):  # Docker interprets a missing file as a directory
            os.removedirs(usage_history_file)
        with open(usage_history_file, "w") as f:
            json.dump({}, f)

    with open(usage_history_file, "r+") as f:
        usage_history = json.load(f)
        # yesterday's date in ISO 8601, e.g. "2022-02-09"import
        usage_history[(datetime.today() - timedelta(days=1)).date().isoformat()] = usage_stats_serializable
        f.seek(0)  # otherwise it will append a complete copy of the usage_history
        json.dump(usage_history, f)
        f.truncate()  # fix if the updated file is smaller than the original

    # cleanup
    context.bot_data['usage_stats']['daily'] = set()
    if datetime.today().strftime("%A").lower() == "monday":
        context.bot_data['usage_stats']['weekly'] = set()
    if datetime.today().day == 1:
        context.bot_data['usage_stats']['monthly'] = set()


def __read_text():
    global text
    with open(file_name, 'r') as f:
        text = f.read()
    text = clean_comments_from_text(text)


def error(update, context):
    """Log Errors caused by Updates."""
    if update:
        # notify user that experienced the error
        if update.effective_message:
            msg = "Hey. I'm sorry to inform you that an error happened while I tried to handle your update. " \
                   "My developer will be notified."
            update.effective_message.reply_text(msg)
        # text the dev
        trace = "".join(traceback.format_tb(sys.exc_info()[2]))
        payload = ""
        # normally, we always have an user. If not, its either a channel or a poll update.
        if update.effective_user:
            payload += " with the user " + str(mention_html(update.effective_user.id, update.effective_user.first_name))
        # there are more situations when you don't get a chat
        if update.effective_chat:
            payload += " within the chat <i>" + str(update.effective_chat.title) + "</i>"
            if update.effective_chat.username:
                payload += " (@" + str(update.effective_chat.username) + ")"
        # but only one where you have an empty payload by now: a poll
        if update.poll:
            payload += " with the poll id " + str(update.poll.id)
        # lets put this in a "well" formatted text
        msg = "Hey.\n The error <code>" + str(context.error) + "</code> happened" + str(payload) + \
              ". The full traceback:\n\n<code>" + str(trace) + "</code>"
        context.bot.send_message(chat_id=castes_chat_id,
                                 text=msg,
                                 parse_mode=HTML)
    raise


class MQBot(Bot):
    """A subclass of Bot which delegates send method handling to MQ"""
    def __init__(self, *args, is_queued_def=True, mqueue=mq.MessageQueue(), **kwargs):
        super(MQBot, self).__init__(*args, **kwargs)
        # below 2 attributes should be provided for decorator usage
        self._is_messages_queued_default = is_queued_def
        self._msg_queue = mqueue

    def __del__(self):
        try:
            self._msg_queue.stop()
        except:
            pass

    @mq.queuedmessage
    def send_message(self, *args, **kwargs):
        """Wrapped method would accept new `queued` and `isgroup` OPTIONAL arguments"""
        return super(MQBot, self).send_message(*args, **kwargs)


def main():
    __read_text()
    set_forbidden_questions()

    def open_db():
        return PicklePersistence(filename='networks_quiz_bot_convo_db')

    try:
        pp = open_db()
    except TypeError:
        old_db_name = "networks_quiz_bot_convo_db.bak_" + str(time())
        os.rename("networks_quiz_bot_convo_db", os.path.join("dbs_old", old_db_name))
        logger.error("The database was corrupted. It has been saved as dbs_old/" + old_db_name +
                     " and has now been reset.")
        pp = open_db()

    updater = Updater(bot=MQBot(token=token,
                                request=Request(con_pool_size=8),
                                mqueue=mq.MessageQueue(all_burst_limit=29, all_time_limit_ms=1020,
                                                       group_burst_limit=19, group_time_limit_ms=60050)),
                      persistence=pp,
                      use_context=True)

    j: JobQueue = updater.job_queue
    # using UTC timezone
    j.run_daily(update_quiz_file,
                time=time(hour=4, minute=0))
    # j.run_daily(handle_usage_stats,
    #             time=time(hour=0, minute=0, second=1))
    j.run_once(handle_usage_stats, when=0)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],

        states={
            CHOOSING_NQ: [
                MessageHandler(Filters.regex('^(' + __change_number_button + ')$'),
                               reply_to_choose_nq,
                               pass_user_data=True),
                MessageHandler(Filters.regex('^(' + __quick_quiz_number_button + '|' +
                                             __exam_sim_covid19_number_button + '|' +
                                             __exam_sim_number_button + ')$'),
                               set_default_number_of_questions,
                               pass_user_data=True)
            ],

            CHANGE_NQ: [
                MessageHandler(Filters.text,
                               choose_number_of_questions,
                               pass_user_data=True)
            ],

            QUIZ: [
                MessageHandler(Filters.regex('^(A|B|C|D|E|F|Skip)$'),
                               quiz_ans,
                               pass_user_data=True),
            ],
        },

        fallbacks=[
            MessageHandler(Filters.regex('^' + __cancel_button + '$'), cancel, pass_user_data=True),
        ],
        name="networks_quiz_bot_convo",
        persistent=True,
        allow_reentry=True
    )

    dp.add_handler(conv_handler)
    dp.add_handler(CommandHandler('help', show_help))
    dp.add_handler(CommandHandler('stats', show_statistics, pass_user_data=True))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
