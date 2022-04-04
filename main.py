import asyncio
import json
import multiprocessing
import os
import threading
import time

import telebot
import websockets
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.environ['API_KEY']
RECIVER = json.loads(os.environ['RECIVER'])

process = None
participants = 0
COUNT_DOWN = 60

bot = telebot.TeleBot(API_KEY)

async def ping():
    global process, participants, COUNT_DOWN, RECIVER
    while True:
        async with websockets.connect(
            "wss://activity-game.binance.com/stream?streams=BUTTON_CLICK"
        ) as websocket:
            response = await websocket.recv()
            response = response.replace("'", '"')
            response = json.loads(response)
            participants = response["data"]["d"]["tp"]
            if process:
                process.terminate()
                sendmsg(
                    f"🔊Someone click the button\nTotal participants: {participants}"
                )
                COUNT_DOWN = 60
            process = multiprocessing.Process(target=count_down, args=(COUNT_DOWN,))
            process.start()


def count_down(COUNT_DOWN):
    global bot
    while COUNT_DOWN != 0:
        s = time.time()
        os.system("cls" if os.name == "nt" else "clear")
        COUNT_DOWN -= 1
        print("Total participants: ", participants)
        print(COUNT_DOWN)
        if COUNT_DOWN < 30:
            msg = threading.Thread(
                target=sendmsg, args=(f"📣📣📣Countdown: {COUNT_DOWN}",)
            )
            msg.start()
        time.sleep(1 - (time.time() - s))


def sendmsg(msg):
    for r in RECIVER:
        bot.send_message(r, msg)

asyncio.get_event_loop().run_until_complete(ping())
