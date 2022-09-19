import os
import telebot
from dotenv import load_dotenv
import datetime


e = datetime.datetime.now()
date="%s-%s-%s" % (e.day, e.month, e.year)
time="%s:%s:%s" % (e.hour, e.minute, e.second)
print(date, time)

# load_dotenv()
# # API key from bot father
# API_KEY = os.getenv('API_KEY')
# # tele chatgroup id
# TELE_CHAT_ID = os.getenv('TELE_CHAT_ID')
# # TELE_CHAT_ID = os.getenv('TELE_TEST_CHAT_ID')

# bot = telebot.TeleBot(API_KEY)

# @bot.message_handler(commands=['Greet'])

# def greet(message):
#     bot.reply_to(message, "Hey! How\'s it going?")

# bot.polling()