from config import * #importamos el token
import telebot #para manejar la API de Telegram

bot = telebot.TeleBot(TELEGRAM_TOKEN)

@bot.message_handler(commands=["start", "inicio"])        #responde al comando start
def Responder_a_Start(message):
    # El bot le da la bienvenida al usuario
    bot.reply_to(message, "Bienvenido a CryptoCompadre, ¿Cómo puedo ayudarte?")


if __name__ == '__main__':
    print('iniciando el bot')
    bot.infinity_polling()
    print('Fin')