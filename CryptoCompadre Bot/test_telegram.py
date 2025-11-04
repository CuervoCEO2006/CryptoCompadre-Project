import sqlite3
from config import TELEGRAM_TOKEN, ALPHA_VANTAGE_API_KEY
import telebot 
import yfinance as yf 
import requests

# 📊 IMPORTACIONES REQUERIDAS PARA GRÁFICOS
import pandas as pd
import matplotlib.pyplot as plt
import io 

# --- CLASE DE FUNCIONALIDAD: NOTICIAS (CORREGIDA) ---
class Noticiero:
    """Clase para obtener noticias financieras utilizando Alpha Vantage."""
    
    BASE_URL = "https://www.alphavantage.co/query"

    def obtener_noticias(self, symbol: str) -> list:
        """
        Obtiene noticias recientes. Se han añadido checks para límites de API.
        """
        # Asegúrate de que esta variable global esté accesible y definida en config.py
        global ALPHA_VANTAGE_API_KEY 
        
        # Alpha Vantage maneja los tickers de crypto sin el -USD y usa 'topics'
        symbol_av = symbol.upper().replace("-USD", "")
        
        params = {
            "function": "NEWS_SENTIMENT", 
            "limit": 5, 
            "apikey": ALPHA_VANTAGE_API_KEY 
        }

        # Alpha Vantage usa el parámetro 'topics' para cryptos y 'tickers' para acciones.
        if symbol in ["BTC-USD", "ETH-USD", "SOL-USD", "ADA-USD", "DOGE-USD"]:
            params["topics"] = "Cryptocurrency"
            # No enviar el parámetro tickers si es crypto para evitar conflictos
        else:
            params["tickers"] = symbol_av
            
        try:
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = requests.get(self.BASE_URL, params=params, timeout=15, headers=headers)
            response.raise_for_status() 
            data = response.json()
            
            # 🔴 VERIFICACIÓN CRÍTICA: Manejo de errores de API
            if "Note" in data:
                 print(f"❌ ATENCIÓN: Alpha Vantage (Límite): {data.get('Note')}. Excediste el límite de llamadas.")
                 return []
            if "Error Message" in data:
                 print(f"❌ ERROR FATAL: Alpha Vantage (Clave): {data.get('Error Message')}. Revisa tu clave API o el símbolo.")
                 return []
            
            noticias_formateadas = []
            
            # 🟢 PROCESAMIENTO NORMAL
            if "feed" in data and isinstance(data["feed"], list):
                for noticia in data["feed"]:
                    title = noticia.get("title")
                    link = noticia.get("url")
                    
                    if title and link:
                         noticias_formateadas.append({
                            "title": title, 
                            "link": link, 
                            "publisher": noticia.get("source", "Fuente desconocida"),
                        })
            
            return noticias_formateadas
            
        except requests.exceptions.HTTPError as http_err:
            print(f"❌ Error HTTP: {http_err}. El símbolo ({symbol}) podría no ser compatible con Alpha Vantage.")
            return []
        except requests.exceptions.RequestException as req_err:
            print(f"❌ Error de CONEXIÓN HTTP al obtener noticias: {req_err}")
            return []
        except Exception as e:
            print(f"❌ Error inesperado en Noticiero: {e}")
            return []


# --- CLASE PRINCIPAL DEL BOT ---
class CryptoCompadre_Bot:

    def __init__(self, TELEGRAM_TOKEN):
        self.bot = telebot.TeleBot(TELEGRAM_TOKEN)
        self.registrar_manejadores()

    def conectar_base_datos(self):
        self.conn = sqlite3.connect('CryptoCompadre.sql')
        self.cursor = self.conn.cursor()

    # 1. FUNCIÓN UNIFICADA DE BIENVENIDA (CON NUEVA IMAGEN DE CONFIANZA)
    def bienvenida_a_usuario(self, message):
        """Envía el mensaje de bienvenida y el menú unificado /compadre con estilo."""
        markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
        
        btn1 = telebot.types.KeyboardButton("🔥 /compadre")
        btn2 = telebot.types.KeyboardButton("🏛️ /syp500") 
        
        markup.row(btn1, btn2)
        
        texto_bienvenida = (
            "**¡Hola, compadre! Soy tu CryptoCompadre!** 🤠\n\n"
            "Soy un bot financiero diseñado para darte **tres datos clave** sobre tus activos favoritos en un solo lugar:\n"
            "1. **Precio Actual** 📈\n"
            "2. **Últimas Noticias** 📰\n"
            "3. **Gráfico Histórico** 📊\n\n"
            "Usa el comando ** /compadre ** para elegir un activo de nuestro menú exclusivo.\n"
            "O usa ** /syp500 ** para ver el índice bursátil más importante de USA.\n\n"
            "**¡Vamos a hacer esos números!** 🚀"
        )
        

        imagen_url = "https://images.pexels.com/photos/6770845/pexels-photo-6770845.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1" 
        
        try:
             self.bot.send_photo(message.chat.id, 
                                imagen_url, 
                                caption=texto_bienvenida, 
                                reply_markup=markup,
                                parse_mode="Markdown")
        except Exception as e:
            # En caso de que falle la foto, enviamos solo el texto (Fallback)
            print(f"❌ Falló el envío de la foto, enviando solo texto. Error: {e}")
            self.bot.send_message(message.chat.id, 
                                  texto_bienvenida, 
                                  reply_markup=markup,
                                  parse_mode="Markdown")


    def obtener_precio_actual(self, chat_id: int, simbolo: str):
        """Consulta el precio actual y devuelve el texto de respuesta."""
        try:
            ticker = yf.Ticker(simbolo)
            data = ticker.info
            
            precio = data.get('regularMarketPrice')
            moneda = data.get('currency', 'USD')
            nombre = data.get('shortName', simbolo)
            cambio_porc = data.get('regularMarketChangePercent')

            if precio is not None:
                etiqueta_cambio = "⬆️ **Subida**" if cambio_porc is not None and cambio_porc > 0 else "⬇️ **Bajada**" if cambio_porc is not None and cambio_porc < 0 else "↔️ **Sin Cambio**"
                emoji_moneda = "₿" if "BTC" in simbolo else "Ξ" if "ETH" in simbolo else "$"
                
                respuesta = f"{emoji_moneda} **PRECIO AL INSTANTE DE {nombre} ({simbolo}):**\n"
                respuesta += f"El precio actual es **{precio:,.2f} {moneda}**.\n"
                
                if cambio_porc is not None:
                    respuesta += f"{etiqueta_cambio}: **{cambio_porc:,.2f}%**."
                
                self.bot.send_message(chat_id, respuesta, parse_mode="Markdown")
                return True
            else:
                self.bot.send_message(chat_id, f"❌ ¡Ups! No se encontró el precio o el símbolo **{simbolo}** no es válido, compadre.")
                return False

        except Exception as e:
            print(f"Error al obtener precio para {simbolo}: {e}")
            self.bot.send_message(chat_id, "Ocurrió un error al buscar el precio. Intenta con otro símbolo, ¡no te rindas!")
            return False

    # 3. FUNCIÓN DE NOTICIAS (SE MANTIENE EL CÓDIGO DE ENVÍO)
    def enviar_noticias(self, chat_id: int, simbolo: str):
        """Obtiene y envía las noticias al chat especificado."""
        try:
            noticiero = Noticiero()
            noticias = noticiero.obtener_noticias(simbolo)
            
            if noticias:
                respuesta = f"🗞️ **Últimas Noticias de {simbolo}** (¡Calientitas!):\n\n"
                NOTICIAS_A_MOSTRAR = 2 
                
                for i, noticia in enumerate(noticias[:NOTICIAS_A_MOSTRAR]): 
                    # Escapar caracteres de Markdown
                    title_escaped = noticia['title'].replace('_', '\\_').replace('*', '\\*').replace('[', '(').replace(']', ')')
                    respuesta += f"**{i+1}.** **[{title_escaped}]({noticia['link']})**\n"
                    respuesta += f"   _✍️ Fuente: {noticia['publisher']}_\n\n"
                
                if len(noticias) > NOTICIAS_A_MOSTRAR:
                    respuesta += f"...\n_Se encontraron {len(noticias) - NOTICIAS_A_MOSTRAR} noticias más, pero no cabían aquí. ¡Busca el enlace!_"

                self.bot.send_message(chat_id, respuesta, parse_mode="Markdown", disable_web_page_preview=True)
            else:
                # Si llega aquí, es porque Noticiero.obtener_noticias devolvió []
                self.bot.send_message(chat_id, f"❌ No se encontraron noticias frescas para **{simbolo}**. ¡El mercado está muy callado! (Revisa la consola por si hay errores de API/Límite de llamadas).")
        
        except Exception as e:
            print(f"Error en enviar_noticias: {e}")
            self.bot.send_message(chat_id, "Ocurrió un error inesperado al buscar las noticias. ¡Revisa tu conexión API!")


    def enviar_grafico(self, chat_id: int, simbolo: str):
        """Genera y envía el gráfico al chat especificado."""
        try:
            generador = GeneradorGraficos()
            imagen_buffer = generador.generar_grafico_precio(simbolo)
            
            if imagen_buffer:
                self.bot.send_photo(chat_id, 
                                     imagen_buffer, 
                                     caption=f"📈 **Gráfico Histórico de {simbolo}** (Últimos 3 meses). ¡Así se ve la tendencia!",
                                     parse_mode="Markdown")
            else:
                self.bot.send_message(chat_id, f"❌ No se pudo generar el gráfico para **{simbolo}**. ¡Quizás el símbolo no tiene datos históricos!")
        except Exception as e:
            print(f"Error en enviar_grafico: {e}")
            self.bot.send_message(chat_id, "Ocurrió un error al generar el gráfico. ¡Problemas con la gráfica!")


    def compadre_menu(self):
        """Crea el teclado inline con los activos principales y sus emojis."""
        markup = telebot.types.InlineKeyboardMarkup()
        tokens = {
            "BTC-USD": "₿ Bitcoin (BTC)",
            "ETH-USD": "Ξ Ethereum (ETH)",
            "AAPL": "🍏 Apple (AAPL)",
            "MSFT": "💻 Microsoft (MSFT)",
            "GOOGL": "🔎 Alphabet (GOOGL)",
            "AMZN": "📦 Amazon (AMZN)",
            "NVDA": "⚡ NVIDIA (NVDA)",
            "META": "🌐 Meta (META)",
            "TSLA": "🚗 Tesla (TSLA)",
            "AVGO": "📶 Broadcom (AVGO)",
            "LLY": "💊 Eli Lilly (LLY)",
            "XOM": "⛽ Exxon Mobil (XOM)",
        }
        
        row = []
        for i, (ticker, nombre_emoji) in enumerate(tokens.items()):
            callback_data = f"DATA_{ticker}" 
            button = telebot.types.InlineKeyboardButton(nombre_emoji, callback_data=callback_data)
            row.append(button)
            
            if (i + 1) % 2 == 0 or i == len(tokens) - 1:
                markup.row(*row)
                row = []
            
        return markup
    
    # -----------------------------------------------------
    # REGISTRO DE MANEJADORES DE COMANDOS
    # -----------------------------------------------------
    def registrar_manejadores(self):
        
        @self.bot.message_handler(commands=["start", "inicio"])
        def responder_a_comandos(message):
            self.bienvenida_a_usuario(message)
            
        @self.bot.message_handler(commands=["syp500"])
        def manejar_syp500(message):
            self.bot.send_message(message.chat.id, "Buscando información del **S&P 500**... 🏛️", parse_mode="Markdown")
            self.obtener_precio_actual(message.chat.id, "^GSPC")
        
        @self.bot.message_handler(commands=["compadre"])
        def manejar_menu_compadre(message):
            menu = self.compadre_menu()
            self.bot.send_message(message.chat.id, 
                                     "🎯 **Selecciona el activo** para el informe completo (Precio, Noticias y Gráfico):",
                                     reply_markup=menu,
                                     parse_mode="Markdown")

        @self.bot.callback_query_handler(func=lambda call: call.data.startswith('DATA_'))
        def callback_inline_unificado(call):
            simbolo = call.data.replace('DATA_', '')
            chat_id = call.message.chat.id
            
            self.bot.edit_message_text(chat_id=chat_id, 
                                         message_id=call.message.message_id, 
                                         text=f"✨ ¡Excelente elección! Buscando tu informe completo de **{simbolo}** (Precio, Noticias y Gráfico)... Dame un momento, compadre. ⏳", 
                                         parse_mode="Markdown")
            
            self.obtener_precio_actual(chat_id, simbolo)
            self.enviar_noticias(chat_id, simbolo)
            self.enviar_grafico(chat_id, simbolo)
            
            self.bot.answer_callback_query(call.id, text=f"✅ Informe de {simbolo} completado. ¡Espero que te sirva, compadre!")

        @self.bot.message_handler(content_types=["text"])
        def responder_mensajes_texto(message):
            self.bot_mensajes_texto(message)

    def bot_mensajes_texto(self, message):
        if message.text.startswith("/"):
            self.bot.send_message(message.chat.id, "❌ **¡Comando incorrecto, mi compadre!** Intenta con /compadre o /syp500. ¡No te vayas por la tangente!")
        else:
            self.bot.send_message(message.chat.id, 
                                     "Recuerda, compadre, **solo me comunico con comandos**, así que no entiendo lo que escribes. ¡Intenta con un comando! 🤝")

    def run(self):
        print("iniciando el bot")
        self.bot.infinity_polling()
        print("fin")


# --- CLASES ADICIONALES (Se mantienen) ---
class Usuario:
    def __init__(self, id_usuario: int, nombre_usuario: str, clave_usuario: str):
        self.id_usuario = id_usuario
        self.nombre_usuario = nombre_usuario
        self.clave_usuario = clave_usuario

class Activo:
    def __init__(self, symbol: str, nombre: str, tipo: str):
        self.symbol = symbol
        self.nombre = nombre
        self.tipo = tipo
        self.precio_actual = 0.0
        self.datos_historicos = []

# 📊 IMPLEMENTACIÓN DE CLASE GENERADOR DE GRÁFICOS
class GeneradorGraficos:
    
    def generar_grafico_precio(self, simbolo: str, period: str = '3mo') -> io.BytesIO | None:
        """
        Genera un gráfico de línea de precios históricos y lo devuelve como buffer de bytes.
        """
        try:
            data = yf.download(simbolo, period=period)
            
            if data.empty:
                return None

            if 'Close' not in data.columns:
                 print(f"Columna 'Close' no encontrada para {simbolo}")
                 return None

            plt.style.use('seaborn-v0_8-darkgrid')
            fig, ax = plt.subplots(figsize=(10, 6))

            data['Close'].plot(ax=ax, color='#007BFF', linewidth=2) 
            
            ax.set_title(f'Precio Histórico de {simbolo} ({period})', fontsize=16, fontweight='bold')
            ax.set_xlabel('Fecha', fontsize=12)
            ax.set_ylabel(f'Precio de Cierre (USD)', fontsize=12)
            ax.tick_params(axis='x', rotation=45)
            plt.tight_layout()

            buffer = io.BytesIO()
            plt.savefig(buffer, format='png', bbox_inches='tight')
            buffer.seek(0)
            plt.close(fig) 
            
            return buffer
        
        except Exception as e:
            print(f"Error al generar gráfico para {simbolo}: {e}")
            return None

    def generar_grafico_comparativo(self, lista_activos):
        pass
        
# -----------------------------------------------------
# PUNTO DE ENTRADA DEL PROGRAMA
# -----------------------------------------------------
if __name__ == '__main__':
    try:
        if 'TELEGRAM_TOKEN' in locals() or 'TELEGRAM_TOKEN' in globals():
             bot = CryptoCompadre_Bot(TELEGRAM_TOKEN)
             bot.run()
        else:
            print("ERROR: La variable TELEGRAM_TOKEN no se cargó desde config.py.")
    except Exception as e:
        print(f"ERROR FATAL AL INICIAR EL BOT: {e}")