from telebot.async_telebot import AsyncTeleBot
from os import environ as envv
import asyncio

bot = AsyncTeleBot(envv['BOT_TOKEN'])

@bot.message_handler(commands=['help','start'])
async def send_welcome(message):
    await bot.reply_to(message,"""hi\ndebil\n""")

asyncio.run(bot.polling())