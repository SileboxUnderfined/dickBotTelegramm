from telebot.async_telebot import AsyncTeleBot, types
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


async def getUserFromDB(user_id, chat_id):
    async with aiosqlite.connect("data.db") as db:
        async with db.execute(f"SELECT user_id, dick_length FROM users WHERE user_id = {user_id} AND chat_id = {chat_id}") as cursor:
            data = await cursor.fetchall()
            if len(data) == 0:
                return False
            result = data[0]
            return result

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


@bot.message_handler(commands=['dice'])
async def dice_func(message):
    text = message.text.split()
    chat_id = message.chat.id
    user_id = message.from_user.id
    if len(text) == 1: await bot.reply_to(message,"Ты не указал ставку!")
    else:
        dick_length = await getUserFromDB(user_id,chat_id)
        if not dick_length:
            await bot.reply_to(message,"сначала отрасти хуй")
            return
        dick_length = dick_length[1]
        bet = int(text[1])
        if bet <= 0:
            await bot.reply_to(message,"поставь ставку с положительным числом.")
            return
        if bet > dick_length:
            await bot.reply_to(message,"У тебя хуй ещё недорос.")
            return

        markup = types.InlineKeyboardMarkup()
        accept_button = types.InlineKeyboardButton('принять приглашение',callback_data="accept_invite")
        markup.add(accept_button)
        await bot.reply_to(message, f"{user_id}\n{await getUserName(chat_id, user_id)} приглашает вас на меряние письками используя шестигранный кубик!\nСтавка: {bet} см\nЧтобы принять приглашение, нажмите на кнопку ниже.",reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data == "accept_invite")
async def accept_invite(call):
    chat_id = call.message.chat.id
    user_id = call.from_user.id
    text = call.message.text.split()
    print(text)
    bet = int(text[text.index("Ставка:")+1])

    sender_id = int(text[0])

    if sender_id == user_id:
        await bot.send_message(chat_id,f"{await getUserName(chat_id,user_id)}, ты не можешь мериться писькой с самим собой.")
        return

    user_dick_length = await getUserFromDB(user_id,chat_id)
    if not user_dick_length:
        await bot.send_message(chat_id,f"{await getUserName(chat_id,user_id)}, сначала отрасти хуй")
        return

    user_dick_length = user_dick_length[1]
    if user_dick_length < bet:
        await bot.send_message(chat_id,f"У {await getUserName(chat_id,user_id)} хуй ещё не дорос чтобы играть в такую ставку.")
        return

    await bot.delete_message(chat_id, call.message.id)
    await bot.send_message(chat_id,f"{await getUserName(chat_id,user_id)} принимает приглашение {await getUserName(chat_id,sender_id)}")
    await bot.send_message(chat_id,'кидаем кубики!')
    user_result = await bot.send_dice(chat_id)
    sender_result = await bot.send_dice(chat_id)
    user_result = int(user_result.dice.value)
    sender_result = int(sender_result.dice.value)
    winner = 0
    looser = 0

    if user_result > sender_result:
        winner = user_id
        looser = sender_id
    elif user_result < sender_result:
        winner = sender_id
        looser = user_id

    if winner == looser:
        await bot.send_message(chat_id,"Никто не победил, письки остаются при вас.")
    else:
        winner_name = await getUserName(chat_id,winner)
        looser_name = await getUserName(chat_id,looser)
        await bot.send_message(chat_id,f"Победил: {winner_name}.\nТеперь {looser_name} отрежут хуй на {bet} см.\nА {winner_name} получит расширение хуя на {bet} см.")
        async with aiosqlite.connect("data.db") as db:
            winner_dick = await getUserFromDB(winner, chat_id)
            looser_dick = await getUserFromDB(looser, chat_id)
            winner_dick = winner_dick[1]
            looser_dick = looser_dick[1]
            await db.execute(f"UPDATE users SET dick_length = {winner_dick+bet} WHERE user_id = {winner} AND chat_id = {chat_id}")
            await db.execute(f"UPDATE users SET dick_length = {looser_dick-bet} WHERE user_id = {looser} AND chat_id = {chat_id}")
            await db.commit()


@bot.message_handler(commands=["my_dick"])
async def my_dick(message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    my_dick = await getUserFromDB(user_id,chat_id)
    if not my_dick:
        await bot.reply_to(message,"отрасти сначала хуй")
        return

    my_dick = my_dick[1]
    await bot.reply_to(message,f"твой хуй равен {my_dick} см")


@bot.message_handler(commands=["global_top"])
async def global_top(message):
    text = f"Глобальный топ {envv['GL_TOP_END']} хуеводов:\n"
    async with aiosqlite.connect("data.db") as db:
        async with db.execute("SELECT user_id, chat_id, dick_length FROM users") as cursor:
            data = await cursor.fetchall()
            data = await getSorted(data)
            print(data)
            start = 0
            end = int(envv['GL_TOP_END'])
            for user in data:
                if start == end: break
                print(user[0])
                try:
                    username = await getUserName(user[1], user[0])
                except Exception:
                    continue

                text += f'{start+1}: {username} - {user[2]} см\n'
                start += 1

    print(text)
    await bot.reply_to(message, text)

asyncio.run(bot.polling())
