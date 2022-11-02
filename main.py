from telebot.async_telebot import AsyncTeleBot
from os import environ as envv
import asyncio

bot = AsyncTeleBot(envv['BOT_TOKEN'])

@bot.message_handler(commands=['start'])
async def send_welcome(message):
    await bot.reply_to(message,"""привет дурак дебильный ебальный\nблагодаря этому боту ты можешь меряться письками с другими дебилами\nчтобы использовать эту бесконечно великую функцию, введи /dick\nвведи /help """)

asyncio.run(bot.polling())