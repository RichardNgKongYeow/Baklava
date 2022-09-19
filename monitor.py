import json
from web3 import Web3
from web3.logs import STRICT, IGNORE, DISCARD, WARN
from typing import List
from multiprocessing import Process, pool
from math import *
# import pandas as pd
import requests
from ast import literal_eval
import time
import decimal
import schedule
import urllib.parse 
import telebot
import logging
# from tronpy import Tron
# from tronpy.providers import HTTPProvider
import constants
import MarginX
import logging
from BaklavaClient.Wrapper import BaklavaClient
from dotenv import load_dotenv
import constants
import os
import datetime 

# from tronpy.providers import HTTPProvider

# ######################################################################################
# Load basic variable
# ######################################################################################

start_time = time.time()

load_dotenv()
# API key from bot father
API_KEY = os.getenv('API_KEY')
# tele chatgroup id
TELE_CHAT_ID = os.getenv('TELE_CHAT_ID')
# TELE_CHAT_ID = os.getenv('TELE_TEST_CHAT_ID')
pair_info = constants.pair_info




# ######################################################################################
# Build core function
# ######################################################################################

def connectRPX():
    global bot
    global bclient
    global client_dict


    bot = telebot.TeleBot(API_KEY)
    
    # initialise wrapper
    my_provider = constants.avax_url
    private_key = os.getenv("PRIVATE_KEY")
    address = constants.wallet_address
    bclient = BaklavaClient(address, private_key, provider=my_provider)


    # initialialise marginX clients
    marginx_account = MarginX.init_wallet(MarginX.seed)
    client_dict = MarginX.initialise_all_clients_and_get_all_info(marginx_account,constants.pair_info)


def greet(message):
    bot.reply_to(message, "Hey! Hows it going")


def queryData():
    global marginx_positions
    global baklava_positions


    global marginx_tsla
    global marginx_aapl
    global marginx_btc

    global baklava_tsla
    global baklava_aapl
    global baklava_btc

    global date_time
    global date
    global _time



    marginx_positions = MarginX.query_all_open_long_positions_amounts(client_dict)
    baklava_positions = bclient.get_syntoken_total_supply()



    marginx_tsla = marginx_positions[pair_info[0]['pair']]
    marginx_aapl = marginx_positions[pair_info[1]['pair']]
    marginx_btc = marginx_positions[pair_info[2]['pair']]



    baklava_tsla = baklava_positions[pair_info[0]['pair']]
    baklava_aapl = baklava_positions[pair_info[1]['pair']]
    baklava_btc = baklava_positions[pair_info[2]['pair']]


    e = datetime.datetime.now()
    date="%s-%s-%s" % (e.day, e.month, e.year)
    _time="%s:%s:%s" % (e.hour, e.minute, e.second)
    date_time = date+_time


def buildTelebotMsg():
    global msgResponse
    global overallResult

    # TSLA token
    if ((marginx_tsla > baklava_tsla)):
        tsla_result = "Warning"
        tsla_description = "MarginX_TSLA > Baklava_TSLA"
        tsla_diff_amount = abs(marginx_tsla-baklava_tsla)
    elif marginx_tsla < baklava_tsla:
        tsla_result = "Warning"
        tsla_description = "MarginX_TSLA < Baklava_TSLA"
        tsla_diff_amount = abs(marginx_tsla - baklava_tsla)
    else:
        tsla_result = "Normal"
        tsla_description = "Both side Equal"
        tsla_diff_amount = abs(marginx_tsla - baklava_tsla)

    # AAPL token
    if ((marginx_aapl > baklava_aapl)):
        aapl_result = "Warning"
        aapl_description = "MarginX_AAPL > Baklava_AAPL"
        aapl_diff_amount = abs(marginx_aapl-baklava_aapl)
    elif marginx_aapl < baklava_aapl:
        aapl_result = "Warning"
        aapl_description = "MarginX_AAPL < Baklava_AAPL"
        aapl_diff_amount = abs(marginx_aapl-baklava_aapl)
    else:
        aapl_result = "Normal"
        aapl_description = "Both side Equal"
        aapl_diff_amount = abs(marginx_aapl-baklava_aapl)

    # BTC token
    if ((marginx_btc > baklava_btc)):
        btc_result = "Warning"
        btc_description = "MarginX_BTC > Baklava_BTC"
        btc_diff_amount = abs(marginx_btc-baklava_btc)
    elif marginx_btc < baklava_btc:
        btc_result = "Warning"
        btc_description = "MarginX_BTC < Baklava_BTC"
        btc_diff_amount = abs(marginx_btc-baklava_btc)
    else:
        btc_result = "Normal"
        btc_description = "Both side Equal"
        btc_diff_amount = abs(marginx_btc-baklava_btc)


    #### Build result msg ####
    if aapl_result == 'Normal' and tsla_result == 'Normal' and btc_result == 'Normal':
        overallResult = "All Normal"
    else:
        overallResult = "Warning"

    # rows0 = [marginx_tsla,marginx_aapl,marginx_btc]
    # rows1 = [baklava_tsla,baklava_aapl,baklava_btc]
    msgResponse = "~~~ Baklava Bridge Daily Report ~~~\n\n"

    msgResponse += f"Baklava Bridge health: {overallResult}\n\n"
    msgResponse += f"Date: {date} Time: {_time}\n\n"

    msgResponse += "~~~~~~~~~~~~ TSLA ~~~~~~~~~~~~\n"
    msgResponse += f"{'MarginX:'.ljust(20)} {'%.2f' % marginx_tsla}\n"
    msgResponse += f"{'Baklava:'.ljust(17)} {'%.2f' % baklava_tsla}\n"
    msgResponse += f"{'Status:'.ljust(21)} {tsla_result}\n"
    msgResponse += f"{'Description:'.ljust(17)} {tsla_description}\n"
    msgResponse += f"{'Diff_Amount:'.ljust(15)} {'%.2f' % tsla_diff_amount}\n\n"

    msgResponse += "~~~~~~~~~~~~ AAPL ~~~~~~~~~~~~\n"
    msgResponse += f"{'MarginX:'.ljust(20)} {'%.2f' % marginx_aapl}\n"
    msgResponse += f"{'Baklava:'.ljust(17)} {'%.2f' % baklava_aapl}\n"
    msgResponse += f"{'Status:'.ljust(21)} {aapl_result}\n"
    msgResponse += f"{'Description:'.ljust(17)} {aapl_description}\n"
    msgResponse += f"{'Diff_Amount:'.ljust(15)} {'%.2f' % aapl_diff_amount}\n\n"
    
    msgResponse += "~~~~~~~~~~~~ BTC ~~~~~~~~~~~~\n"
    msgResponse += f"{'MarginX:'.ljust(20)} {'%.2f' % marginx_btc}\n"
    msgResponse += f"{'Baklava:'.ljust(17)} {'%.2f' % baklava_btc}\n"
    msgResponse += f"{'Status:'.ljust(21)} {btc_result}\n"
    msgResponse += f"{'Description:'.ljust(17)} {btc_description}\n"
    msgResponse += f"{'Diff_Amount:'.ljust(15)} {'%.2f' % btc_diff_amount}\n\n"


    if aapl_result != 'Normal' or tsla_result != 'Normal' or btc_result != 'Normal':
        bot.send_message(TELE_CHAT_ID, msgResponse)

def sendTeleReport():
    bot.send_message(TELE_CHAT_ID, msgResponse)


# ######################################################################################
# Build flow function
# ######################################################################################

def minCheck():
    try:
        queryData()
        buildTelebotMsg()
    except Exception as e:
        print("minCheck Error happen")
        logging.error(e)

def dailyReport():
    try:
        queryData()
        buildTelebotMsg()
    except Exception as e:
        print("dailyReport Error happen")
        logging.error(e)
    else:
        sendTeleReport()

def listenTeleMsg():
    try:
        @bot.message_handler(commands=['data'])
        def echo_all(message):
            bot.reply_to(message, "Here comes the latest data...")
            dailyReport()
        bot.infinity_polling()
    except Exception as e:
        print("listenTele Error")
        logging.error(e)
        main()

# ######################################################################################
# Build schedule function
# ######################################################################################

def scheduleDailyReport():
    schedule.every().minutes.do(minCheck)
    schedule.every().day.at("07:00").do(dailyReport)
    while True:
        schedule.run_pending()
        time.sleep(1)

# ********************
# Main function
# ********************

def main():
    connectRPX()

    queryData()
    buildTelebotMsg()
    sendTeleReport()

    print("--- %s seconds ---" % (time.time() - start_time))
    scheduleDailyReport()

if __name__ == "__main__":     # __name__ is a built-in variable in Python which evaluates to the name of the current module.
    main()
