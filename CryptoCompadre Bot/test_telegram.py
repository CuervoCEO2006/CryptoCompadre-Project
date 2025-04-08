from config import * #importamos el token
import telebot #para manejar la API de Telegram

bot = telebot.TeleBot(TELEGRAM_TOKEN)

@bot.message_handler(commands=["start", "inicio"])        #responde al comando start
def Responder_a_Comandos(message):
    # El bot le da la bienvenida al usuario
    bot.reply_to(message, "Bienvenido a CryptoCompadre, ¿Cómo puedo ayudarte?")


@bot.message_handler(content_types=["text"])
def responder_mensajes_texto(message):
    if message.text.startswith("/"):
        bot.send_message(message.chat.id, "Comando incorrecto, compadre ")

    else:
        bot.send_message(message.chat.id, "Recuerda, compadre, solo me comunico con comandos,"
                                       " así que no entiendo lo que dices. ¡Intenta con un comando!")




    #el atributo que recibe este objeto message es para registrar
    # el id unico del chat de telegram con el usuario.
    # El otro parámetro es el mensaje que responderá el bot a los mensajes de texto del usuario que no sean comandos.
if __name__ == '__main__':
    print('iniciando el bot')
    bot.infinity_polling()
    print('Fin')