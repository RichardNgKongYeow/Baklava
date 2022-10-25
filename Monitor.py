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
import logging
import Clients
from dotenv import load_dotenv
import os
import datetime
import asyncio
import utils
from Marginx import MarginX
from Configs import Pairs


# ######################################################################################
# Load basic variable
# ######################################################################################


class MonitorBot():

    CLIENT_NAME = "MonitorBot"

    def __init__(self, API_KEY, TELE_CHAT_ID, baklava_client, client_dict):

        self.API_KEY = API_KEY
        self.baklava_client = baklava_client
        self.marginx_client_dict = client_dict
        self.bot = telebot.TeleBot(API_KEY)
        self.TELE_CHAT_ID = TELE_CHAT_ID

    async def query_all_data(self):
        try:

            marginx_positions = await MarginX.query_all_open_long_positions_amounts(self.marginx_client_dict)
            print(marginx_positions)
            baklava_positions = self.baklava_client.get_syntoken_total_supply()

            e = datetime.datetime.now()
            date = "%s-%s-%s" % (e.day, e.month, e.year)
            _time = "%s:%s:%s" % (e.hour, e.minute, e.second)
            # date_time = date+_time

            return marginx_positions, baklava_positions, date, _time

        except Exception as e:
            logging.error("{},query_all_data,{},{}".format(
                self.CLIENT_NAME, e, type(e)))


# ######################################################################################
# Build core function
# ######################################################################################


    def check_pair(self, chain_id: str, marginx_positions: dict, baklava_positions: dict) -> tuple:
        try:

            pair_id = self.baklava_client.configs['chain_id'][chain_id]['pair_id']

            marginx_name = self.baklava_client.configs['chain_id'][chain_id]['MarginX']
            baklava_name = self.baklava_client.configs['chain_id'][chain_id]['Baklava']

            marginx_amount = marginx_positions[pair_id]
            baklava_amount = baklava_positions[pair_id]

            if ((marginx_amount > baklava_amount)):
                result = "Warning"
                description = "{} > {}".format(marginx_name, baklava_name)
                diff_amount = abs(marginx_amount-baklava_amount)
                direction = "MarketSell"
            elif marginx_amount < baklava_amount:
                result = "Warning"
                description = "{} < {}".format(marginx_name, baklava_name)
                diff_amount = abs(marginx_amount - baklava_amount)
                direction = "MarketBuy"
            else:
                result = "Normal"
                description = "Both side Equal"
                diff_amount = abs(marginx_amount - baklava_amount)
                direction = None

            pair_info = {
                "pair_id": pair_id,
                "marginx_amount": marginx_amount,
                "baklava_amount": baklava_amount,
                "result": result,
                "description": description,
                "diff_amount": diff_amount,
                "direction": direction

            }

            return pair_info
        except Exception as e:
            logging.error("{},check_pair,{},{}".format(
                self.CLIENT_NAME, e, type(e)))

    async def min_check(self):
        try:
            marginx_positions, baklava_positions, date, _time = await self.query_all_data()

            all_data = {}
            for chain_id in Pairs.chain_ids:
                pair_info = self.check_pair(
                    chain_id, marginx_positions, baklava_positions)
                all_data[chain_id] = pair_info

            """
            {chain_id:{
            "pair_id":pair_id,
            "marginx_amount":marginx_amount,
            "baklava_amount":baklava_amount,
            "result":result,
            "description":description,
            "diff_amount":diff_amount,
            "direction":direction
            }}
            """
            return all_data, date, _time
        except Exception as e:
            logging.error("{},min_check,{},{}".format(
                self.CLIENT_NAME, e, type(e)))


# ######################################################################################
# Build telebot function  (can add other ways to read data)
# ######################################################################################


    async def buildTelebotMsg(self):

        try:
            all_data, date, _time = await self.min_check()

            tsla_result = all_data['tsla']['result']
            marginx_tsla = all_data['tsla']['marginx_amount']
            baklava_tsla = all_data['tsla']['baklava_amount']
            tsla_description = all_data['tsla']['description']
            tsla_diff_amount = all_data['tsla']['diff_amount']

            aapl_result = all_data['aapl']['result']
            marginx_aapl = all_data['aapl']['marginx_amount']
            baklava_aapl = all_data['aapl']['baklava_amount']
            aapl_description = all_data['aapl']['description']
            aapl_diff_amount = all_data['aapl']['diff_amount']

            btc_result = all_data['btc']['result']
            marginx_btc = all_data['btc']['marginx_amount']
            baklava_btc = all_data['btc']['baklava_amount']
            btc_description = all_data['btc']['description']
            btc_diff_amount = all_data['btc']['diff_amount']

            wfx_result = all_data['fx']['result']
            marginx_wfx = all_data['fx']['marginx_amount']
            baklava_wfx = all_data['fx']['baklava_amount']
            wfx_description = all_data['fx']['description']
            wfx_diff_amount = all_data['fx']['diff_amount']

            eth_result = all_data['eth']['result']
            marginx_eth = all_data['eth']['marginx_amount']
            baklava_eth = all_data['eth']['baklava_amount']
            eth_description = all_data['eth']['description']
            eth_diff_amount = all_data['eth']['diff_amount']

            #### Build result msg ####
            if tsla_result == 'Normal' and aapl_result == 'Normal' and btc_result == 'Normal' and wfx_result == 'Normal' and eth_result == 'Normal':
                overallResult = "All Normal"
            else:
                overallResult = "Warning"

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

            msgResponse += "~~~~~~~~~~~~ WFX ~~~~~~~~~~~~\n"
            msgResponse += f"{'MarginX:'.ljust(20)} {'%.2f' % marginx_wfx}\n"
            msgResponse += f"{'Baklava:'.ljust(17)} {'%.2f' % baklava_wfx}\n"
            msgResponse += f"{'Status:'.ljust(21)} {wfx_result}\n"
            msgResponse += f"{'Description:'.ljust(17)} {wfx_description}\n"
            msgResponse += f"{'Diff_Amount:'.ljust(15)} {'%.2f' % wfx_diff_amount}\n\n"

            msgResponse += "~~~~~~~~~~~~ ETH ~~~~~~~~~~~~\n"
            msgResponse += f"{'MarginX:'.ljust(20)} {'%.2f' % marginx_eth}\n"
            msgResponse += f"{'Baklava:'.ljust(17)} {'%.2f' % baklava_eth}\n"
            msgResponse += f"{'Status:'.ljust(21)} {wfx_result}\n"
            msgResponse += f"{'Description:'.ljust(17)} {eth_description}\n"
            msgResponse += f"{'Diff_Amount:'.ljust(15)} {'%.2f' % eth_diff_amount}\n\n"

            if aapl_result != 'Normal' or tsla_result != 'Normal' or btc_result != 'Normal' or wfx_result != 'Normal' or eth_result != 'Normal':
                self.bot.send_message(self.TELE_CHAT_ID, msgResponse)

        except Exception as e:
            logging.error("{},buildTelebotMsg,{},{}".format(
                self.CLIENT_NAME, e, type(e)))

    # def dailyReport():
    #     try:
    #         queryData()
    #         buildTelebotMsg()
    #     except Exception as e:

    #         logging.error("Monitoring bot--failed to run daily report due to: {} of type {}".format(e,type(e)))
    #     else:
    #         sendTeleReport()


# ######################################################################################
# Build executor function
# ######################################################################################
    # TODO function not built fully

    async def add_event_to_queue(pair_id, direction, converted_amount, myQueue):
        """
        get event vars from smart contract listener and put it in the queue
        """

        # signature: AAPL:USDT MarketBuy 8802 101
        # await myQueue.put((pair_id, direction, amount, order_id))
        order_id = 0
        converted_price = 0
        amount = utils.to3dp(converted_amount)
        await myQueue.put((pair_id, direction, amount, order_id))
        # converted_price = utils.fromWei(price)
        # converted_amount = utils.from3dp(amount)
        logging.info("Monitoring Bot--Listening to order of Pair: {}, Direction: {}, Price: {}, Amount: {}, OrderId: {}".format(
            pair_id, direction, converted_price, converted_amount, order_id))


# ######################################################################################
# Build schedule function
# ######################################################################################

async def scheduleDailyReport(monitor_bot):
    try:
        while True:
            await monitor_bot.buildTelebotMsg()
            time.sleep(30)
    except Exception as e:
        logging.error("{},scheduleDailyReport,{},{}".format(
            monitor_bot.CLIENT_NAME, e, type(e)))

    # schedule.every(1).minutes.do(monitor_bot.buildTelebotMsg)

    # # schedule.every().day.at("07:00").do(dailyReport)
    # while True:
    #     schedule.run_pending()

    #     time.sleep(1)

# ********************
# Main function
# ********************


async def main():

    # start_time = time.time()
    # initialise configs and logging
    configs = Clients.initialise_configs()
    Clients.initialise_logging(configs['monitor_client_logs_file'])
    load_dotenv()

    # initialise clients
    baklava_client = Clients.initialise_baklava_client(configs)
    client_dict = Clients.initialise_marginx_client(configs)
    load_dotenv()
    # API key from bot father
    API_KEY = os.getenv('API_KEY')
    # tele chatgroup id
    TELE_CHAT_ID = os.getenv('TELE_CHAT_ID')
    # TELE_CHAT_ID = os.getenv('TELE_TEST_CHAT_ID')
    monitor_bot = MonitorBot(API_KEY, TELE_CHAT_ID,
                             baklava_client, client_dict)

    # queryData()
    await scheduleDailyReport(monitor_bot)
    # sendTeleReport()

    # print("--- %s seconds ---" % (time.time() - start_time))


# __name__ is a built-in variable in Python which evaluates to the name of the current module.
if __name__ == "__main__":
    asyncio.run(main())
