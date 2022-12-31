from os import environ as envv
from random import randint
from telebot.async_telebot import types
from datetime import datetime, timedelta
from quickchart import QuickChart
import sys, aiosqlite, signal

timeFormat = "%Y%m%d%H%M%S"

def exit_handler(sig, frame):
    print('exiting...')
    sys.exit(0)


async def genrand():
    result = 0
    while result == 0: result = randint(int(envv['start_rand']),int(envv['end_rand']))
    return result


async def getNextTime():
    r = datetime.now() + timedelta(hours=int(envv['KD']))
    return r.strftime(timeFormat)


async def getDateTime(s):
    return datetime.strptime(s,timeFormat)


def topSort(x):
    return x[1]


async def getSorted(data):
    return list(reversed(sorted(data, key=topSort)))


async def getUserInfo(bot, chat_id,user_id):
    return await bot.get_chat_member(chat_id, user_id)


async def getUserName(bot, chat_id, user_id):
    user_info = await getUserInfo(bot, chat_id, user_id)
    if user_info.user.username == None: return user_info.user.first_name
    return user_info.user.username

async def getUserId(bot, chat_id, username):
    async with aiosqlite.connect('data.db') as db:
        async with db.execute(f"SELECT user_id FROM users WHERE chat_id = {chat_id}") as cursor:
            data = await cursor.fetchall()
            for user in data:
                nick = await getUserName(bot, chat_id, user[0])
                if nick == username:
                    return user[0]

async def createQC(data):
    qc = QuickChart()
    qc.width = 500
    qc.height = 300
    qc.device_pixel_ratio = 2
    qc.config = {
        "type": "pie",
        "data": {
            "labels": [key for key in data.keys()],
            "datasets": [
                {
                    "data": [value for value in data.values()]
                }
            ]
        }
    }
    return qc.get_url()


async def getDickFO(now_dick=0):
    new_dick = await genrand()
    choice = randint(0,3)
    result: int
    if choice == 1:
        result = now_dick * new_dick
        operation = "*"
    elif choice == 2 and now_dick != 0:
        result = round(now_dick // new_dick)
        operation = "//"
    elif choice == 3 and now_dick != 0:
        result = now_dick ** new_dick
        operation = '^'
    else:
        result = now_dick + new_dick
        operation = "+"

    print(operation)
    if result < 0: result = 0
    elif result > now_dick + 100: result = now_dick + 100
    return new_dick, round(result), operation

async def getDick(now_dick=0):
    new_dick = await genrand()
    result = now_dick + new_dick
    if result < 0: result = 0
    return new_dick, result

async def getDickNE(now_dick=0):
    new_dick = randint(1,20)
    result = now_dick + new_dick
    return new_dick, result

async def getUserFromDB(user_id, chat_id):
    async with aiosqlite.connect("data.db") as db:
        async with db.execute(f"SELECT user_id, dick_length FROM users WHERE user_id = {user_id} AND chat_id = {chat_id}") as cursor:
            data = await cursor.fetchall()
            if len(data) == 0:
                return False
            result = data[0]
            return result

async def add_chat_to_table(chat_id, admin_id):
    async with aiosqlite.connect("data.db") as db:
        async with db.execute(f"SELECT * FROM chats WHERE chat_id={chat_id}") as cursor:
            data = await cursor.fetchall()
            if len(data) > 0: return
        await db.execute(f"INSERT INTO chats (chat_id, fancy_operations, admin) VALUES ({chat_id},0,{admin_id})")
        await db.commit()

async def check_fancy_ops(chat_id):
    async with aiosqlite.connect("data.db") as db:
        async with db.execute(f"SELECT fancy_operations FROM chats WHERE chat_id = {chat_id}") as cursor:
            data = await cursor.fetchall()
            data = data[0][0]
            if data == 0: return False

    return True

signal.signal(signal.SIGINT, exit_handler)