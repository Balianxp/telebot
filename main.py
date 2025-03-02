import os
import logging
from flask import Flask, request
from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
import asyncio

# Configuração de Logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constantes
class Config:
    TOKEN = "7778588441:AAGlW5V6_CA9f6ZcYNM0MgSxXkt7ZVmBojs"
    ADMIN_ID = 6206033489
    WEBHOOK_URL = os.environ.get("WEBHOOK_URL", "https://brunaluiza-bot.onrender.com/webhook")

# Inicialização
app = Flask(__name__)
bot = Bot(token=Config.TOKEN, parse_mode=ParseMode.MARKDOWN)
dp = Dispatcher()

# Teclado Principal
def main_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Planos VIP 💎")],
            [KeyboardButton(text="Packs Exclusivos 🔥")],
            [KeyboardButton(text="Conteúdos Grátis 🥵")]
        ],
        resize_keyboard=True
    )

# Handler do /start
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    logger.info(f"Recebido /start de {message.from_user.id}")
    try:
        await message.answer(
            f"🔥 *Oi, {message.from_user.first_name}! Eu sou a Lulu, sua priminha mais safada!*\n\n"
            "Você caiu no meu cantinho secreto pra ver o que ninguém mais vê 😈\n"
            "Escolha agora ou vai ficar só na vontade:",
            reply_markup=main_menu()
        )
        logger.info(f"Resposta enviada para {message.from_user.id}")
    except Exception as e:
        logger.error(f"Erro ao responder /start: {str(e)}")

# Webhook
@app.route("/webhook", methods=["POST"])
def webhook():
    logger.info("Requisição recebida no webhook")
    if request.headers.get("content-type") == "application/json":
        update = types.Update(**request.get_json())
        # Processa a atualização em uma tarefa assíncrona no loop global
        asyncio.ensure_future(dp.feed_update(bot, update))
        return "OK"
    else:
        logger.warning("Requisição inválida no webhook")
        return "", 403

# Configuração do Webhook na Inicialização
async def set_webhook():
    await bot.delete_webhook(drop_pending_updates=True)  # Limpa qualquer webhook antigo
    await bot.set_webhook(Config.WEBHOOK_URL)
    logger.info(f"Webhook configurado: {Config.WEBHOOK_URL}")

# Função principal pra manter o loop ativo
async def main():
    await set_webhook()
    # Mantém o loop rodando indefinidamente
    while True:
        await asyncio.sleep(3600)  # Dorme por 1 hora pra manter o loop ativo

# Inicialização
if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    asyncio.set_event_loop(loop)
    # Inicia o Flask em uma thread separada
    port = int(os.environ.get("PORT", 5000))
    logger.info(f"Iniciando Flask na porta {port}")
    from threading import Thread
    def run_flask():
        app.run(host="0.0.0.0", port=port)
    flask_thread = Thread(target=run_flask)
    flask_thread.start()
    # Executa a função principal no loop asyncio
    loop.run_until_complete(main())