from os import environ as envv
from random import randint
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


async def createQC(data):
    qc = QuickChart()
    qc.width = 500
    qc.height = 300
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


async def getDick(now_dick=0):
    new_dick = await genrand()
    result = now_dick + new_dick
    if result < 0: result = 0
    return new_dick, result


async def getUserFromDB(user_id, chat_id):
    async with aiosqlite.connect("data.db") as db:
        async with db.execute(f"SELECT user_id, dick_length FROM users WHERE user_id = {user_id} AND chat_id = {chat_id}") as cursor:
            data = await cursor.fetchall()
            if len(data) == 0:
                return False
            result = data[0]
            return result

signal.signal(signal.SIGINT, exit_handler)