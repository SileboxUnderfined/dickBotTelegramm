from telebot.async_telebot import AsyncTeleBot
from os import environ as envv
import asyncio, aiosqlite, signal, sys
from random import randint
from datetime import datetime, timedelta
from quickchart import QuickChart

bot = AsyncTeleBot(envv['BOT_TOKEN'])
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

async def getUserInfo(chat_id,user_id):
    return await bot.get_chat_member(chat_id, user_id)

async def getUserName(chat_id, user_id):
    user_info = await getUserInfo(chat_id, user_id)
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

signal.signal(signal.SIGINT, exit_handler)

@bot.message_handler(commands=['start'])
async def send_welcome(message):
    await bot.reply_to(message,"""привет дурак дебильный ебальный\nблагодаря этому боту ты можешь меряться письками с другими дебилами\nчтобы использовать эту бесконечно великую функцию, введи /dick\nвведи /help """)
    print('/start command for', message.from_user)

@bot.message_handler(commands=['dick'])
async def dick_func(message):
    next_time = await getNextTime()
    user_id = int(message.from_user.id)
    chat_id = int(message.chat.id)
    async with aiosqlite.connect("data.db") as db:
        async with db.execute(f"SELECT * FROM users WHERE user_id = {user_id} AND chat_id = {chat_id}") as cursor:
            data = await cursor.fetchall()
            print(data)
            if len(data) == 0:
                print([element for element in data])
                new_dick, r = await getDick()
                await db.execute(f"INSERT INTO users (user_id, dick_length, next_date, chat_id) VALUES ({user_id},{r}, {next_time}, {message.chat.id})")
                await db.commit()
                await bot.reply_to(message, f"Тебе создали новый хуй, поздравляю. Он равен {r} см.")
            else:
                async with db.execute(f"SELECT next_date FROM users WHERE user_id = {user_id} AND chat_id={chat_id}") as ct:
                    next_timeU = await ct.fetchone()
                    next_timeU = await getDateTime(next_timeU[0])

                nowDate = datetime.now()
                delta = next_timeU - nowDate
                r = str(timedelta(seconds=delta.seconds)).split(":")
                if nowDate < next_timeU:
                    await bot.reply_to(message, f"Ты идиот. Жди ещё {r[0]} часов, {r[1]} минут и {r[2]} секунд")
                else:
                    now_dick = [user[2] for user in data if user[1] == user_id][0]
                    new_dick, r = await getDick(now_dick)
                    await db.execute(f"UPDATE users SET dick_length = {r} WHERE user_id = {user_id} AND chat_id={chat_id}")
                    await db.execute(f"UPDATE users SET next_date = {next_time} WHERE user_id = {user_id} AND chat_id={chat_id}")
                    await db.commit()
                    await bot.reply_to(message, f"Твой хер был обновлён на {new_dick}, поздравляю. Сейчас он равен {r}")
    print("/dick command for ", user_id)

@bot.message_handler(commands=["top"])
async def top_func(message):
    chat_id = message.chat.id
    async with aiosqlite.connect("data.db") as db:
        async with db.execute(f"SELECT user_id, dick_length FROM users WHERE chat_id = {chat_id}") as cursor:
            data = await cursor.fetchall()
            if len(data) == 0: await bot.reply_to(message,"вы пока не призывали письки")
            else:
                data = await getSorted(data)

                result = f"Топ лучших:\n"
                for user in range(len(data)):
                    result += f"{user+1}: {await getUserName(chat_id,data[user][0])} с хуём в размере {data[user][1]} см\n"
                await bot.reply_to(message,result)

@bot.message_handler(commands=["graph"])
async def graph_func(message):
    chat_id = message.chat.id
    async with aiosqlite.connect("data.db") as db:
        async with db.execute(f"SELECT user_id, dick_length FROM users WHERE chat_id = {chat_id}") as cursor:
            data = await cursor.fetchall()
            if len(data) == 0: await bot.reply_to(message,"вы пока не призывали письки")
            else:
                data = await getSorted(data)
                dfg = {}
                for user in data:
                    dfg.update({await getUserName(chat_id,user[0]):user[1]})

                url = await createQC(dfg)
                await bot.send_photo(chat_id, url)


asyncio.run(bot.polling())