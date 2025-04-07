from config import * #importamos el token
import telebot #para manejar la API de Telegram


class Bot:
    bot = telebot.TeleBot(TELEGRAM_TOKEN)