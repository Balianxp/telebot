import os
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from flask import Flask, request, abort
from datetime import datetime
import asyncio

# ============= CONFIGURAÇÕES INICIAIS =============
# Configuração de Logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constantes
class Config:
    TOKEN = "7778588441:AAGlW5V6_CA9f6ZcYNM0MgSxXkt7ZVmBojs"  # Token do bot
    ADMIN_ID = 6206033489  # Seu ID no Telegram
    VIP_GROUP = "https://t.me/+qYv4s2q0AQBjYTVh"  # Grupo VIP
    PREVIEW_GROUP = "https://t.me/lulupriminha"   # Grupo de prévias
    INSTAGRAM = "https://www.instagram.com/lulupriminha"  # Instagram
    SUPPORT_BOT = "@brunaluizahot"  # Botão de suporte para comprovantes
    BOT_USERNAME = "@BrunaLuiza_Bot"  # Remarketing e promoções
    WEBHOOK_URL = os.environ.get("WEBHOOK_URL", "https://brunaluiza-bot.onrender.com/webhook")  # URL do Render
    PIX_NUMBER = "31984952759"  # Sua chave Pix
    PIX_NAME = "Bruna Luiza Barbosa"  # Nome associado ao Pix

# Inicialização do Bot e Dispatcher
bot = Bot(token=Config.TOKEN, parse_mode=ParseMode.MARKDOWN)
dp = Dispatcher()

# Inicialização do Flask
app = Flask(__name__)

# ============= BANCO DE DADOS EM MEMÓRIA =============
class Database:
    plans = {
        "1_week": {"name": "1 SEMANA", "price": 19.90, "duration": 7, "description": "🔥 Um gostinho do meu lado mais quente direto no seu celular!"},
        "1_month": {"name": "1 MÊS", "price": 59.90, "duration": 30, "description": "30 dias pra você se perder nos meus segredos 😈"},
        "6_months": {"name": "6 MESES", "price": 119.90, "duration": 180, "description": "Me veja peladinha todo dia por 6 meses, aguenta?"},
        "12_months": {"name": "12 MESES VIP", "price": 199.90, "duration": 365, "description": "💎 Acesso total: vídeos, chamadas e mimos só pra você!"}
    }
    
    packs = {
        "basic": {"name": "PACK BÁSICO", "price": 29.90, "description": "3 fotos + 3 vídeos de me pegar de jeito 😏"},
        "advanced": {"name": "PACK AVANÇADO", "price": 59.90, "description": "5 fotos + 5 vídeos com meus brinquedos favoritos 🍆💦"},
        "premium": {"name": "PACK PREMIUM", "price": 99.90, "description": "10 fotos + 10 quartos com gemidos que você não esquece 🥵"}
    }
    
    users = {}
    subscriptions = {}

# ============= TELAS DO BOT =============
class Keyboards:
    @staticmethod
    def main_menu():
        return ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="Planos VIP 💎")],
                [KeyboardButton(text="Packs Exclusivos 🔥")],
                [KeyboardButton(text="Conteúdos Grátis 🥵")]
            ],
            resize_keyboard=True
        )
    
    @staticmethod
    async def plans_menu():
        builder = InlineKeyboardBuilder()
        for plan_id, plan in Database.plans.items():
            builder.button(
                text=f"{plan['name']} - R${plan['price']}",
                callback_data=f"plan:{plan_id}"
            )
        builder.adjust(1)
        return builder.as_markup()
    
    @staticmethod
    async def packs_menu():
        builder = InlineKeyboardBuilder()
        for pack_id, pack in Database.packs.items():
            builder.button(
                text=f"{pack['name']} - R${pack['price']}",
                callback_data=f"pack:{pack_id}"
            )
        builder.adjust(1)
        return builder.as_markup()
    
    @staticmethod
    def free_content_menu():
        builder = InlineKeyboardBuilder()
        builder.button(text="👥 GRUPO DE PRÉVIAS", url=Config.PREVIEW_GROUP)
        builder.button(text="📸 MEU INSTAGRAM", url=Config.INSTAGRAM)
        builder.button(text="🔥 QUERO MAIS!", url=f"https://t.me/{Config.BOT_USERNAME}")
        builder.adjust(1)
        return builder.as_markup()
    
    @staticmethod
    def confirmation_buttons():
        builder = InlineKeyboardBuilder()
        builder.button(text="✅ PAGAMENTO FEITO", callback_data="confirm_payment")
        builder.button(text="📲 SUPORTE", url=f"https://t.me/{Config.SUPPORT_BOT}")
        builder.button(text="❌ CANCELAR", callback_data="cancel")
        builder.adjust(1)
        return builder.as_markup()

# ============= LÓGICA PRINCIPAL =============
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    logger.info(f"Recebido /start de {message.from_user.id}")
    user_id = message.from_user.id
    Database.users[user_id] = {"last_interaction": datetime.now()}
    try:
        await message.answer(
            f"🔥 *Oi, {message.from_user.first_name}! Eu sou a Lulu, sua priminha mais safada!*\n\n"
            "Você caiu no meu cantinho secreto pra ver o que ninguém mais vê 😈\n"
            "Escolha agora ou vai ficar só na vontade:",
            reply_markup=Keyboards.main_menu()
        )
        logger.info(f"Resposta enviada para {user_id}")
    except Exception as e:
        logger.error(f"Erro ao responder /start para {user_id}: {str(e)}")

@dp.message(lambda message: message.text == "Planos VIP 💎")
async def show_plans(message: types.Message):
    logger.info(f"Planos VIP solicitado por {message.from_user.id}")
    await message.answer(
        "💎 *MEU VIP É PRA QUEM AGUENTA O CALOR*\n\n"
        "Quanto tempo você quer me ter todinha pra você?",
        reply_markup=await Keyboards.plans_menu()
    )

@dp.message(lambda message: message.text == "Packs Exclusivos 🔥")
async def show_packs(message: types.Message):
    logger.info(f"Packs solicitado por {message.from_user.id}")
    await message.answer(
        "🔥 *PACKS QUE VÃO TE DEIXAR LOUCO*\n\n"
        "Escolhe logo o que quer ver hoje:",
        reply_markup=await Keyboards.packs_menu()
    )

@dp.message(lambda message: message.text == "Conteúdos Grátis 🥵")
async def show_free_content(message: types.Message):
    logger.info(f"Conteúdos grátis solicitado por {message.from_user.id}")
    await message.answer(
        "🥵 *SÓ UM GOSTINHO DO QUE EU GUARDO...*\n\n"
        "Quer mais? Então vem comigo:",
        reply_markup=Keyboards.free_content_menu()
    )

@dp.callback_query(lambda callback: callback.data.startswith("plan:"))
async def handle_plan_selection(callback: types.CallbackQuery):
    logger.info(f"Plano selecionado por {callback.from_user.id}: {callback.data}")
    plan_id = callback.data.split(":")[1]
    plan = Database.plans.get(plan_id)
    payment_info = (
        f"💎 *PLANO {plan['name'].upper()}*\n\n"
        f"Valor: R${plan['price']}\n"
        f"Duração: {plan['duration']} dias\n"
        f"Descrição: {plan['description']}\n\n"
        "⚠️ *FAÇA O PIX AGORA:*\n"
        f"*Chave:* `{Config.PIX_NUMBER}`\n"
        f"*Nome:* {Config.PIX_NAME}`\n\n"
        "Pagou? Clica em 'PAGAMENTO FEITO' e manda o comprovante pro suporte!"
    )
    await callback.message.answer(payment_info, reply_markup=Keyboards.confirmation_buttons())
    await callback.answer()

@dp.callback_query(lambda callback: callback.data.startswith("pack:"))
async def handle_pack_selection(callback: types.CallbackQuery):
    logger.info(f"Pack selecionado por {callback.from_user.id}: {callback.data}")
    pack_id = callback.data.split(":")[1]
    pack = Database.packs.get(pack_id)
    payment_info = (
        f"🔥 *{pack['name'].upper()}*\n\n"
        f"Valor: R${pack['price']}\n"
        f"Descrição: {pack['description']}\n\n"
        "⚠️ *FAÇA O PIX AGORA:*\n"
        f"*Chave:* `{Config.PIX_NUMBER}`\n"
        f"*Nome:* {Config.PIX_NAME}`\n\n"
        "Pagou? Clica em 'PAGAMENTO FEITO' e manda o comprovante pro suporte!"
    )
    await callback.message.answer(payment_info, reply_markup=Keyboards.confirmation_buttons())
    await callback.answer()

@dp.callback_query(lambda callback: callback.data == "confirm_payment")
async def confirm_payment(callback: types.CallbackQuery):
    logger.info(f"Confirmação de pagamento por {callback.from_user.id}")
    await callback.message.answer(
        f"📸 *Beleza, agora é comigo!*\n"
        f"Manda o comprovante pro suporte [{Config.SUPPORT_BOT}](https://t.me/{Config.SUPPORT_BOT}) que eu libero seu acesso na hora! 🔥"
    )
    await callback.answer()

@dp.callback_query(lambda callback: callback.data == "cancel")
async def cancel_payment(callback: types.CallbackQuery):
    logger.info(f"Cancelamento por {callback.from_user.id}")
    await callback.message.answer(
        "❌ *Sem problemas, se mudar de ideia é só voltar aqui!*\n"
        f"Quer tentar de novo? Fala comigo: [{Config.BOT_USERNAME}](https://t.me/{Config.BOT_USERNAME}) 😏"
    )
    await callback.answer()

@dp.message(lambda message: message.photo or message.document)
async def handle_proof(message: types.Message):
    logger.info(f"Comprovante recebido de {message.from_user.id}")
    user_id = message.from_user.id
    await message.answer(
        "💦 *Comprovante recebido!*\n"
        f"Vou verificar rapidinho e liberar tudo pra você. Qualquer coisa, fala com o suporte: [{Config.SUPPORT_BOT}](https://t.me/{Config.SUPPORT_BOT})!"
    )
    await bot.send_message(
        Config.ADMIN_ID,
        f"✅ Novo pagamento de {message.from_user.first_name} (ID: {user_id})"
    )
    await bot.forward_message(Config.ADMIN_ID, message.from_user.id, message.message_id)

# ============= PROMOÇÃO AUTOMÁTICA =============
async def send_promo():
    while True:
        try:
            await bot.send_message(
                Config.PREVIEW_GROUP.split("https://t.me/")[1],
                f"⚡ *HOJE TEM PROMO MALUCA: 50% OFF NO PACK BÁSICO!* Só R$14,95.\n"
                f"Corre pra pegar o seu antes que acabe: [{Config.BOT_USERNAME}](https://t.me/{Config.BOT_USERNAME}) 🔥",
                parse_mode=ParseMode.MARKDOWN
            )
            logger.info("Promoção enviada ao grupo de prévias")
        except Exception as e:
            logger.error(f"Erro ao enviar promoção: {str(e)}")
        await asyncio.sleep(86400)  # 24 horas

# ============= CONFIGURAÇÃO WEBHOOK =============
@app.route("/webhook", methods=["POST"])
def webhook():
    logger.info("Requisição recebida no webhook")
    if request.headers.get("content-type") == "application/json":
        update = types.Update(**request.get_json())
        asyncio.run_coroutine_threadsafe(dp.feed_update(bot, update), loop)
        return "OK"
    else:
        logger.warning("Requisição inválida no webhook")
        abort(403)

async def set_webhook():
    try:
        await bot.set_webhook(Config.WEBHOOK_URL)
        logger.info(f"Webhook configurado com sucesso: {Config.WEBHOOK_URL}")
    except Exception as e:
        logger.error(f"Erro ao configurar webhook: {str(e)}")

async def startup():
    await set_webhook()
    asyncio.create_task(send_promo())

# ============= INICIALIZAÇÃO =============
if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(startup())
    port = int(os.environ.get("PORT", 5000))
    logger.info(f"Iniciando Flask na porta {port}")
    app.run(host="0.0.0.0", port=port)