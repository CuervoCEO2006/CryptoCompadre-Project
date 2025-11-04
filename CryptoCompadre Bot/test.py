# Ejemplo de prueba en tu código (podrías ejecutar esto fuera de Telegram primero)
import yfinance as yf

# PRUEBA 1: Acción
ticker_aapl = yf.Ticker("AAPL")
noticias_aapl = ticker_aapl.news
print(f"Noticias para AAPL ({len(noticias_aapl)} encontradas):")
# print(noticias_aapl) # Descomenta para ver la respuesta completa

# PRUEBA 2: Criptomoneda
ticker_btc = yf.Ticker("BTC-USD")
noticias_btc = ticker_btc.news
print(f"\nNoticias para BTC-USD ({len(noticias_btc)} encontradas):")
# print(noticias_btc) # Descomenta para ver la respuesta completa