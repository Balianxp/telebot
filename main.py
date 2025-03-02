import os
import logging
from aiogram import Bot, Dispatcher, types, executor
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from datetime import datetime, timedelta
import asyncio

# Configuração de Logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constantes
class Config:
    TOKEN = "7778588441:AAGlW5V6_CA9f6ZcYNM0MgSxXkt7ZVmBojs"
    ADMIN_ID = 6206033489
    WEBHOOK_URL = os.environ.get("WEBHOOK_URL", "https://brunaluiza-bot.onrender.com/webhook")
    VIP_GROUP = "https://t.me/+qYv4s2q0AQBjYTVh"
    PREVIEW_GROUP = "https://t.me/lulupriminha"
    INSTAGRAM = "https://www.instagram.com/lulupriminha"
    SUPPORT_BOT = "@brunaluizahot"
    BOT_USERNAME = "@BrunaLuiza_Bot"
    PIX_NUMBER = "31984952759"
    PIX_NAME = "Bruna Luiza Barbosa"

# Inicialização
bot = Bot(token=Config.TOKEN, parse_mode=ParseMode.MARKDOWN)
dp = Dispatcher(bot)

# Banco de Dados em Memória
class Database:
    plans = {
        "1_week": {"name": "1 SEMANA", "price": 19.90, "duration": 7, "description": "🔥 Um gostinho do meu lado mais quente direto no seu celular!"},
        "1_month": {"name": "1 MÊS", "price": 59.90, "duration": 30, "description": "30 dias pra você se perder nos meus segredos 😈"},
        "6_months": {"name": "6 MESES", "price": 119.90, "duration": 180, "description": "Me veja peladinha todo dia por 6 meses, aguenta?"},
        "12_months": {"name": "12 MESES VIP", "price": 199.90, "duration": 365, "description": "💎 Acesso total: vídeos, chamadas e mimos só pra você!"}
    }
    
    packs = {
        "basic": {"name": "PACK BÁSICO", "price": 29.90, "description": "3 fotos + 3 vídeos de me pegar de jeito 😏", "preview": "🔍 Veja um teaser: 1 foto sensual inclusa!"},
        "advanced": {"name": "PACK AVANÇADO", "price": 59.90, "description": "5 fotos + 5 vídeos com meus brinquedos favoritos 🍆💦", "preview": "🔍 Amostra: 1 vídeo curtinho inclusa!"},
        "premium": {"name": "PACK PREMIUM", "price": 99.90, "description": "10 fotos + 10 vídeos com gemidos que você não esquece 🥵", "preview": "🔍 Spoiler: 1 foto + 1 gemido pra te deixar louco!"}
    }
    
    users = {}  # {user_id: {"last_interaction": datetime, "subscriptions": {"plan_id": {"start": datetime, "end": datetime}}}}
    pending_payments = {}  # {user_id: {"type": "plan/pack", "id": "plan_id/pack_id", "timestamp": datetime}}

# Teclados
class Keyboards:
    @staticmethod
    def main_menu(is_admin=False):
        keyboard = [
            [KeyboardButton(text="Planos VIP 💎")],
            [KeyboardButton(text="Packs Exclusivos 🔥")],
            [KeyboardButton(text="Conteúdos Grátis 🥵")]
        ]
        if is_admin:
            keyboard.append([KeyboardButton(text="Admin: Editar Bot ⚙️")])
        return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)

    @staticmethod
    def plans_menu():
        builder = InlineKeyboardBuilder()
        for plan_id, plan in Database.plans.items():
            builder.button(text=f"{plan['name']} - R${plan['price']}", callback_data=f"plan:{plan_id}")
        builder.adjust(1)
        return builder.as_markup()

    @staticmethod
    def packs_menu():
        builder = InlineKeyboardBuilder()
        for pack_id, pack in Database.packs.items():
            builder.button(text=f"{pack['name']} - R${pack['price']}", callback_data=f"pack:{pack_id}")
        builder.adjust(1)
        return builder.as_markup()

    @staticmethod
    def free_content_menu():
        builder = InlineKeyboardBuilder()
        builder.button(text="👥 GRUPO DE PRÉVIAS", url=Config.PREVIEW_GROUP)
        builder.button(text="📸 MEU INSTAGRAM", url=Config.INSTAGRAM)
        builder.button(text="🔥 QUERO MAIS!", callback_data="upsell_main")
        builder.adjust(1)
        return builder.as_markup()

    @staticmethod
    def confirmation_buttons(item_type, item_id):
        builder = InlineKeyboardBuilder()
        builder.button(text="✅ PAGAMENTO FEITO", callback_data=f"confirm:{item_type}:{item_id}")
        builder.button(text="📲 SUPORTE", url=f"https://t.me/{Config.SUPPORT_BOT}")
        builder.button(text="❌ CANCELAR", callback_data=f"cancel:{item_type}:{item_id}")
        builder.adjust(1)
        return builder.as_markup()

    @staticmethod
    def admin_menu():
        builder = InlineKeyboardBuilder()
        builder.button(text="Editar Planos", callback_data="admin_plans")
        builder.button(text="Editar Packs", callback_data="admin_packs")
        builder.button(text="Ver Assinantes", callback_data="admin_users")
        builder.adjust(1)
        return builder.as_markup()

# Handlers
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    user_id = message.from_user.id
    Database.users[user_id] = {"last_interaction": datetime.now(), "subscriptions": Database.users.get(user_id, {}).get("subscriptions", {})}
    is_admin = user_id == Config.ADMIN_ID
    logger.info(f"Recebido /start de {user_id}")
    await message.answer(
        f"🔥 *Oi, {message.from_user.first_name}! Eu sou a Lulu, sua priminha mais safada!*\n\n"
        "Você caiu no meu cantinho secreto pra ver o que ninguém mais vê 😈\n"
        "Escolha agora e vem sentir o calor:",
        reply_markup=Keyboards.main_menu(is_admin)
    )

@dp.message(lambda message: message.text == "Planos VIP 💎")
async def show_plans(message: types.Message):
    await message.answer(
        "💎 *MEU VIP É PRA QUEM AGUENTA O FOGO!*\n\n"
        "Quanto tempo você quer me ter só pra você? Escolhe agora:",
        reply_markup=Keyboards.plans_menu()
    )

@dp.message(lambda message: message.text == "Packs Exclusivos 🔥")
async def show_packs(message: types.Message):
    await message.answer(
        "🔥 *PACKS QUE VÃO TE LEVAR AO DELÍRIO!*\n\n"
        "Olha só o que eu preparei pra você hoje:",
        reply_markup=Keyboards.packs_menu()
    )

@dp.message(lambda message: message.text == "Conteúdos Grátis 🥵")
async def show_free_content(message: types.Message):
    await message.answer(
        "🥵 *SÓ UM GOSTINHO DO QUE EU GUARDO...*\n\n"
        "Quer mais? Então vem comigo agora:",
        reply_markup=Keyboards.free_content_menu()
    )

@dp.message(lambda message: message.text == "Admin: Editar Bot ⚙️" and message.from_user.id == Config.ADMIN_ID)
async def admin_panel(message: types.Message):
    await message.answer("⚙️ *Painel Admin - O que você quer ajustar?*", reply_markup=Keyboards.admin_menu())

@dp.callback_query(lambda callback: callback.data.startswith("plan:"))
async def handle_plan_selection(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    plan_id = callback.data.split(":")[1]
    plan = Database.plans.get(plan_id)
    payment_info = (
        f"💎 *PLANO {plan['name'].upper()}*\n\n"
        f"Valor: R${plan['price']}\n"
        f"Duração: {plan['duration']} dias\n"
        f"Descrição: {plan['description']}\n\n"
        "⚠️ *FAÇA O PIX AGORA E GARANTA SEU LUGAR!*\n"
        f"*Chave:* `{Config.PIX_NUMBER}`\n"
        f"*Nome:* {Config.PIX_NAME}`\n\n"
        "Pagou? Clica em 'PAGAMENTO FEITO' e manda o comprovante pro suporte!"
    )
    Database.pending_payments[user_id] = {"type": "plan", "id": plan_id, "timestamp": datetime.now()}
    await callback.message.answer(payment_info, reply_markup=Keyboards.confirmation_buttons("plan", plan_id))
    await callback.answer()

@dp.callback_query(lambda callback: callback.data.startswith("pack:"))
async def handle_pack_selection(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    pack_id = callback.data.split(":")[1]
    pack = Database.packs.get(pack_id)
    payment_info = (
        f"🔥 *{pack['name'].upper()}*\n\n"
        f"Prévia: {pack['preview']}\n"
        f"Valor: R${pack['price']}\n"
        f"Descrição: {pack['description']}\n\n"
        "⚠️ *FAÇA O PIX AGORA E LEVE ESSE PACOTE QUENTE!*\n"
        f"*Chave:* `{Config.PIX_NUMBER}`\n"
        f"*Nome:* {Config.PIX_NAME}`\n\n"
        "Tá esperando o quê? Clica em 'PAGAMENTO FEITO' e me manda o comprovante!"
    )
    Database.pending_payments[user_id] = {"type": "pack", "id": pack_id, "timestamp": datetime.now()}
    await callback.message.answer(payment_info, reply_markup=Keyboards.confirmation_buttons("pack", pack_id))
    await callback.answer()

@dp.callback_query(lambda callback: callback.data.startswith("confirm:"))
async def confirm_payment(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    item_type, item_id = callback.data.split(":")[1:]
    if user_id in Database.pending_payments and Database.pending_payments[user_id]["id"] == item_id:
        await callback.message.answer(
            f"📸 *Perfeito, {callback.from_user.first_name}!*\n"
            f"Manda o comprovante pro suporte [{Config.SUPPORT_BOT}](https://t.me/{Config.SUPPORT_BOT}) agora que eu libero tudo rapidinho! 🔥"
        )
    await callback.answer()

@dp.callback_query(lambda callback: callback.data.startswith("cancel:"))
async def cancel_payment(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    item_type, item_id = callback.data.split(":")[1:]
    if user_id in Database.pending_payments and Database.pending_payments[user_id]["id"] == item_id:
        del Database.pending_payments[user_id]
        await callback.message.answer(
            "❌ *Sem crise, se mudar de ideia eu te espero!*\n"
            f"Quer tentar de novo? Clica aqui: [{Config.BOT_USERNAME}](https://t.me/{Config.BOT_USERNAME}) 😏",
            reply_markup=Keyboards.main_menu()
        )
    await callback.answer()

@dp.callback_query(lambda callback: callback.data == "upsell_main")
async def upsell_main(callback: types.CallbackQuery):
    await callback.message.answer(
        "🔥 *Tá gostando do gostinho? Imagina o que eu guardo no VIP e nos Packs!*\n\n"
        "Não deixa pra depois, escolhe agora e vem pro fogo comigo:",
        reply_markup=Keyboards.main_menu()
    )
    await callback.answer()

@dp.message(lambda message: message.photo or message.document)
async def handle_proof(message: types.Message):
    user_id = message.from_user.id
    if user_id in Database.pending_payments:
        item_type = Database.pending_payments[user_id]["type"]
        item_id = Database.pending_payments[user_id]["id"]
        if item_type == "plan":
            start_time = datetime.now()
            duration = Database.plans[item_id]["duration"]
            end_time = start_time + timedelta(days=duration)
            Database.users[user_id]["subscriptions"][item_id] = {"start": start_time, "end": end_time}
            await message.answer(
                f"💦 *Aprovado, {message.from_user.first_name}!*\n"
                f"Seu plano {Database.plans[item_id]['name']} tá liberado! Entra no VIP agora: [{Config.VIP_GROUP}]({Config.VIP_GROUP})\n"
                "Quer mais? Confira os Packs Exclusivos 🔥",
                reply_markup=Keyboards.main_menu()
            )
            await bot.send_message(Config.ADMIN_ID, f"✅ Novo plano ativado: {message.from_user.first_name} (ID: {user_id}) - {item_id}")
        elif item_type == "pack":
            await message.answer(
                f"💦 *Liberado, {message.from_user.first_name}!*\n"
                "Seu {Database.packs[item_id]['name']} tá a caminho! Vou te enviar por DM agora.\n"
                "Que tal entrar no VIP pra mais? 👇",
                reply_markup=Keyboards.main_menu()
            )
            await bot.send_message(Config.ADMIN_ID, f"✅ Novo pack vendido: {message.from_user.first_name} (ID: {user_id}) - {item_id}")
        del Database.pending_payments[user_id]

# Admin Commands
@dp.callback_query(lambda callback: callback.data == "admin_plans" and callback.from_user.id == Config.ADMIN_ID)
async def admin_edit_plans(callback: types.CallbackQuery):
    plans_text = "\n".join([f"{plan_id}: {plan['name']} - R${plan['price']} ({plan['duration']} dias)" for plan_id, plan in Database.plans.items()])
    await callback.message.answer(
        f"⚙️ *Editar Planos*\n\nPlanos atuais:\n{plans_text}\n\n"
        "Envie no formato: /edit_plan <id> <nome> <preço> <duração> <descrição>\n"
        "Exemplo: /edit_plan 1_week Novo Plano 29.90 7 Novo teste quente!"
    )
    await callback.answer()

@dp.callback_query(lambda callback: callback.data == "admin_packs" and callback.from_user.id == Config.ADMIN_ID)
async def admin_edit_packs(callback: types.CallbackQuery):
    packs_text = "\n".join([f"{pack_id}: {pack['name']} - R${pack['price']}" for pack_id, pack in Database.packs.items()])
    await callback.message.answer(
        f"⚙️ *Editar Packs*\n\nPacks atuais:\n{packs_text}\n\n"
        "Envie no formato: /edit_pack <id> <nome> <preço> <descrição> <prévia>\n"
        "Exemplo: /edit_pack basic Novo Pack 39.90 5 fotos quentes 1 foto teaser"
    )
    await callback.answer()

@dp.message(Command("edit_plan"))
async def edit_plan(message: types.Message):
    if message.from_user.id != Config.ADMIN_ID:
        return
    try:
        _, plan_id, name, price, duration, *description = message.text.split()
        description = " ".join(description)
        Database.plans[plan_id] = {"name": name, "price": float(price), "duration": int(duration), "description": description}
        await message.answer(f"✅ Plano {plan_id} atualizado com sucesso!")
    except Exception as e:
        await message.answer(f"❌ Erro: {str(e)}. Use o formato correto!")

@dp.message(Command("edit_pack"))
async def edit_pack(message: types.Message):
    if message.from_user.id != Config.ADMIN_ID:
        return
    try:
        _, pack_id, name, price, *rest = message.text.split()
        description = " ".join(rest[:-1])
        preview = rest[-1]
        Database.packs[pack_id] = {"name": name, "price": float(price), "description": description, "preview": preview}
        await message.answer(f"✅ Pack {pack_id} atualizado com sucesso!")
    except Exception as e:
        await message.answer(f"❌ Erro: {str(e)}. Use o formato correto!")

# Remarketing e Expiração
async def check_expirations():
    while True:
        now = datetime.now()
        for user_id, data in list(Database.users.items()):
            for plan_id, sub in list(data["subscriptions"].items()):
                if now > sub["end"]:
                    del data["subscriptions"][plan_id]
                    await bot.send_message(
                        user_id,
                        f"⏰ *Seu plano {Database.plans[plan_id]['name']} expirou!*\n"
                        "Volta pro calor do VIP agora ou pega um Pack Exclusivo pra não perder nada: 👇",
                        reply_markup=Keyboards.main_menu()
                    )
                    await bot.send_message(Config.ADMIN_ID, f"🔔 Assinatura de {user_id} ({plan_id}) expirou.")
        for user_id, pending in list(Database.pending_payments.items()):
            if (now - pending["timestamp"]).total_seconds() > 3600:  # 1 hora
                del Database.pending_payments[user_id]
                await bot.send_message(
                    user_id,
                    f"⏳ *Ei, {user_id}! Tá esperando o quê?*\n"
                    "Você não terminou sua compra... Volta agora e garante o seu: 👇",
                    reply_markup=Keyboards.main_menu()
                )
        await asyncio.sleep(3600)  # Verifica a cada hora

# Configuração do Webhook na Inicialização
async def on_startup(_):
    await bot.delete_webhook(drop_pending_updates=True)
    await bot.set_webhook(Config.WEBHOOK_URL)
    logger.info(f"Webhook configurado: {Config.WEBHOOK_URL}")
    asyncio.create_task(check_expirations())

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    executor.start_webhook(
        dispatcher=dp,
        webhook_path="/webhook",
        on_startup=on_startup,
        skip_updates=True,
        host="0.0.0.0",
        port=port
    )