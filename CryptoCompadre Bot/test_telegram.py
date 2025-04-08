from config import * #importamos el token
import telebot #para manejar la API de Telegram

class CryptoCompadre_Bot:

    def __init__(self, TELEGRAM_TOKEN):
        self.bot = telebot.TeleBot(TELEGRAM_TOKEN)
        self.responder_comando()

    def responder_comando(self):
        @self.bot.message_handler(commands=["start", "inicio"])
        def responder_a_comandos(message):
            self.bienvenida_a_usuario(message)

        @self.bot.message_handler(content_types=["text"])
        def responder_mensajes_texto(message):
            self.bot_mensajes_texto(message)

    def bienvida_a_usuario(self, message):
        self.bot.reply_to(message,"Bienvenido al Bot CriptoCompadre, ¿Cómo puedo ayudarte?")









