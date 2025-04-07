from config import * #importamos el token
import telebot #para manejar la API de Telegram


class Bot:
    def __init__(self, TELEGRAM_TOKEN):
        self.bot = telebot.TeleBot(TELEGRAM_TOKEN)

