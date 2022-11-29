import telebot.async_telebot as tb
from telebot.async_telebot import AsyncTeleBot, types
import asyncio, logging, os
from botFuncs import *

bot = AsyncTeleBot(envv['BOT_TOKEN'])

@bot.message_handler(commands=['start'])
async def send_welcome(message):

    await bot.reply_to(message,"""привет дурак дебильный ебальный\nблагодаря этому боту ты можешь меряться письками с другими дебилами\nчтобы использовать эту бесконечно великую функцию, введи /dick\nвведи /help """)

@bot.my_chat_member_handler()
async def handleStart(data):
    chat_id = data.chat.id
    admins = await bot.get_chat_administrators(chat_id)
    admin_id = admins[0].user.id
    await add_chat_to_table(chat_id=chat_id, admin_id=admin_id)

@bot.message_handler(commands=['dick'])
async def dick_func(message):
    next_time = await getNextTime()
    user_id = int(message.from_user.id)
    chat_id = int(message.chat.id)
    if user_id == chat_id:
        await bot.reply_to(message, "ты не можешь делать это в лс с самим собой")
        return

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
                return

        async with db.execute(f"SELECT next_date FROM users WHERE user_id = {user_id} AND chat_id={chat_id}") as ct:
            next_timeU = await ct.fetchone()
            next_timeU = await getDateTime(next_timeU[0])

        nowDate = datetime.now()
        delta = next_timeU - nowDate
        r = str(timedelta(seconds=delta.seconds)).split(":")
        if nowDate < next_timeU:
            await bot.reply_to(message, f"Ты идиот. Жди ещё {r[0]} часов, {r[1]} минут и {r[2]} секунд")
            return

        now_dick = [user[2] for user in data if user[1] == user_id][0]
        fancyOps = await check_fancy_ops(chat_id)
        if fancyOps:
            new_dick, r, operation = await getDickFO(now_dick)
        else:
            new_dick, r = await getDick(now_dick)
        await db.execute(f"UPDATE users SET dick_length = {r} WHERE user_id = {user_id} AND chat_id={chat_id}")
        await db.execute(f"UPDATE users SET next_date = {next_time} WHERE user_id = {user_id} AND chat_id={chat_id}")
        await db.commit()
        if fancyOps:
            await bot.reply_to(message, f"Твой хер был обновлён на {operation}{new_dick}, поздравляю. Сейчас он равен {r}")
            return
        await bot.reply_to(message, f"Твой хер был обновлён на {new_dick}, поздравляю. Сейчас он равен {r}")
    print("/dick command for ", user_id)


@bot.message_handler(commands=["top"])
async def top_func(message):
    chat_id = message.chat.id
    totaldick = 0
    async with aiosqlite.connect("data.db") as db:
        async with db.execute(f"SELECT user_id, dick_length FROM users WHERE chat_id = {chat_id}") as cursor:
            data = await cursor.fetchall()
            if len(data) == 0:
                await bot.reply_to(message,"вы пока не призывали письки")
                return
            data = await getSorted(data)

            result = f"Топ лучших:\n"
            for user in range(len(data)):
                result += f"{user+1}: {await getUserName(bot, chat_id,data[user][0])} с хуём в размере {data[user][1]} см\n"
                totaldick += int(data[user][1])

            result += f'Тотальный хуй: {totaldick}'
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
                    dfg.update({await getUserName(bot, chat_id,user[0]):user[1]})

                url = await createQC(dfg)
                await bot.send_photo(chat_id, url)


@bot.message_handler(commands=['dice'])
async def dice_func(message):
    text = message.text.split()
    chat_id = message.chat.id
    user_id = message.from_user.id
    if len(text) == 1:
        await bot.reply_to(message,"Ты не указал ставку!")
        return

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
    await bot.reply_to(message, f"{user_id}\n{await getUserName(bot, chat_id, user_id)} приглашает вас на меряние письками используя шестигранный кубик!\nСтавка: {bet} см\nЧтобы принять приглашение, нажмите на кнопку ниже.",reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data == "accept_invite")
async def accept_invite(call):
    chat_id = call.message.chat.id
    user_id = call.from_user.id
    text = call.message.text.split()
    print(text)
    bet = int(text[text.index("Ставка:")+1])

    sender_id = int(text[0])

    if sender_id == user_id:
        await bot.send_message(chat_id,f"{await getUserName(bot, chat_id,user_id)}, ты не можешь мериться писькой с самим собой.")
        return

    user_dick_length = await getUserFromDB(user_id,chat_id)
    sender_dick_length = await getUserFromDB(sender_id, chat_id)
    if not user_dick_length:
        await bot.send_message(chat_id,f"{await getUserName(bot, chat_id,user_id)}, сначала отрасти хуй")
        return

    if not sender_dick_length:
        await bot.send_message(chat_id,f"{await getUserName(bot, chat_id,sender_id)}, сначала отрасти хуй")
        return

    user_dick_length = user_dick_length[1]
    sender_dick_length = sender_dick_length[1]
    if user_dick_length < bet:
        await bot.send_message(chat_id,f"У {await getUserName(bot, chat_id,user_id)} хуй ещё не дорос чтобы играть в такую ставку.")
        return

    if sender_dick_length < bet:
        await bot.send_message(chat_id,f"У {await getUserName(bot, chat_id,sender_id)} хуй ещё не дорос чтобы играть в такую ставку.")
        return

    await bot.delete_message(chat_id, call.message.id)
    await bot.send_message(chat_id,f"{await getUserName(bot, chat_id,user_id)} принимает приглашение {await getUserName(bot, chat_id,sender_id)}")
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
        return

    winner_name = await getUserName(bot, chat_id,winner)
    looser_name = await getUserName(bot, chat_id,looser)
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
    globalDick = 0
    async with aiosqlite.connect("data.db") as db:
        async with db.execute("SELECT user_id, dick_length, chat_id FROM users") as cursor:

            data = await cursor.fetchall()
            data = await getSorted(data)
            print(data)
            start = 0
            end = int(envv['GL_TOP_END'])
            for user in data:
                if start == end: break
                if user[0] == user[2]: continue
                print(user[0])
                try:
                    username = await getUserName(bot, user[2], user[0])
                except Exception:
                    continue
                async with db.execute(f"SELECT fancy_operations FROM chats WHERE chat_id = {user[2]}") as c1:
                    fanops = await c1.fetchall()
                    fanops = fanops[0][0]
                    isfanops = 'выкл'
                    if fanops == 1:
                        isfanops = 'вкл'
                text += f'{start+1}: {username} - {user[1]} см. Еб. Оп. {isfanops}\n'
                globalDick += int(user[1])
                start += 1

    print(text)
    text += f'Глобальный хуй: {globalDick} см.'
    await bot.reply_to(message, text)

@bot.message_handler(commands=["fancy_ops"])
async def fancy_ops(message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    admins = await bot.get_chat_administrators(chat_id)
    admin_id = admins[0].user.id
    if user_id != admin_id:
        await bot.reply_to(message, "ты не админ, ты не можешь изменять эту настройку")
        return

    async with aiosqlite.connect("data.db") as db:
        async with db.execute(f"SELECT fancy_operations FROM chats WHERE chat_id = {chat_id}") as cursor:
            data = await cursor.fetchall()
            print(data)
            if len(data) == 0:
                await add_chat_to_table(chat_id, admin_id)
                await bot.reply_to(message, "множество других операций у вашей беседы выключено")
                return

        what_to_set = 0
        what_to_say = 'выключены'
        if data[0][0] == 0:
            what_to_set = 1
            what_to_say = 'включены'

        await db.execute(f"UPDATE chats SET fancy_operations = {what_to_set} WHERE chat_id = {chat_id}")
        await db.commit()

    await bot.reply_to(message, f"Дополнительные операции {what_to_say}")

@bot.message_handler(commands=['give_dick'])
async def give_dick_func(message):
    text = message.text.split()
    user_id = message.from_user.id
    chat_id = message.chat.id
    reciever_nick = text[2].replace('@',"")
    if len(text) == 1:
        await bot.reply_to(message, 'ты не указал размер дарования!')
        return

    elif len(text) == 2:
        await bot.reply_to(message, 'ты не указал получателя')
        return

    dick_length = await getUserFromDB(user_id, chat_id)
    if not dick_length:
        await bot.reply_to(message, 'сначала отрасти хуй')
        return

    dick_length = dick_length[1]
    amount = int(text[1])

    if amount <= 0:
        await bot.reply_to(message, 'укажи положительный размер')
        return

    if amount > dick_length:
        await bot.reply_to(message, 'сначала отрасти хуй')
        return

    reciever = await getUserId(bot, chat_id, reciever_nick)
    reciever_dick = await getUserFromDB(reciever, chat_id)
    reciever_dick = reciever_dick[1]
    if reciever == user_id:
        await bot.reply_to(message, 'ты не можешь делиться хуём с самим собой')
        return

    async with aiosqlite.connect('data.db') as db:
        await db.execute(f"UPDATE users SET dick_length = {dick_length - amount} WHERE user_id = {user_id} AND chat_id = {chat_id}")
        await db.execute(f"UPDATE users SET dick_length = {reciever_dick + amount} WHERE user_id = {reciever} AND chat_id = {chat_id}")
        await db.commit()

    await bot.reply_to(message, f'Теперь у {reciever_nick} хуй равен {reciever_dick + amount}\nА у тебя теперь хуй равен {dick_length - amount}')

if __name__ in "__main__":
    logger = tb.logger
    tb.logger.setLevel(logging.DEBUG)
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    if not os.path.isdir('logs'):
        os.mkdir('logs')
    tb.logger.addHandler(logging.FileHandler(os.path.join('logs', f"{now}.log")))

    asyncio.run(bot.polling())