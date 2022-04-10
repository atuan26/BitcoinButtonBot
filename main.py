import asyncio
import json
import multiprocessing
import os
import threading
import time

from telebot.async_telebot import AsyncTeleBot
import telebot
import websockets
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.environ['API_KEY']
RECIVER = json.loads(os.environ['RECIVER'])
COUNT_DOWN_NOTIFY = int(os.environ['COUNT_DOWN_NOTIFY'])

process = None
participants = 0
COUNT_DOWN = 60

bot = telebot.TeleBot(API_KEY)
abot = AsyncTeleBot(API_KEY)

async def ping():
    await asyncio.sleep(3)
    print('ping')
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
                    f"🔊Someone click the button\nTotal participants: {participants} [ Check!](https://www.binance.com/en/activity/bitcoin-button-game)"
                )
                COUNT_DOWN = 60
            process = multiprocessing.Process(target=count_down, args=(COUNT_DOWN,))
            process.start()


def count_down(COUNT_DOWN):
    global bot
    while COUNT_DOWN != 0:
        s = time.time()
        # os.system("cls" if os.name == "nt" else "clear")
        COUNT_DOWN -= 1
        print("Total participants: ", participants)
        print(COUNT_DOWN)
        if COUNT_DOWN < COUNT_DOWN_NOTIFY:
            msg = threading.Thread(
                target=sendmsg, args=(f"[📣📣📣Countdown:  {COUNT_DOWN}](https://www.binance.com/en/activity/bitcoin-button-game)",)
            )
            msg.start()
        time.sleep(1 - (time.time() - s))


def sendmsg(msg):
    for r in RECIVER:
        bot.send_message(r, msg, parse_mode='Markdown', disable_web_page_preview=True)


@abot.message_handler(commands=['greet'])
async def send_welcome(message):
    await abot.reply_to(message, "Howdy, how are you doing?")

loop = asyncio.get_event_loop() 
loop.create_task(ping())
loop.run_until_complete(abot.polling())

try:
    loop.run_forever()
except KeyboardInterrupt:
    pass
