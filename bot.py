import logging
import asyncio
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
    ConversationHandler,
)

# Configuración básica de logs
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

# ================= CONFIGURACIÓN =================
# Pega aquí el token que te dio BotFather para @Goldenprono_bot
TOKEN = '8766310204:AAHkES2jKcfLv3mrM8gUO1u784x7NNnayzU'

# Pon aquí tu ID de usuario de Telegram (para que el bot sepa quién es el "jefazo" que aprueba los pagos)
# Puedes averiguarlo escribiendo a bots como @userinfobot en Telegram.
ADMIN_ID = 8616456713  

# Link del grupo o canal privado al que entrarán al pagar
ENLACES_VIP = [
    "https://t.me/+V-6SNixn5_k4ZDUx", # STAKE Y RETOS
    "https://t.me/+V-6SNixn5_k4ZDUx", # EXCLUSIVO GALLITO + JAPO ....
    "https://t.me/+mx1yX6lzGFY0NzUx", # TIPSTERS OCTUBRE
    "https://t.me/+ch02zWL1U-g2MjVh", # ALTA EFECTIVIDAD
]
# =================================================

# Estados para la conversación de agregar promos
PEDIR_INFO_PROMO = range(1)

PROMOS_ACTIVAS = [
    (
        "🔥 **GRUPO PREMIUM DE GOLDEN BOY PICKS**\n\n"
        "TE INCLUYE 5 GRUPOS:\n"
        "• MEXICANOS 🇲🇽\n"
        "• ALTA EFECTIVIDAD 📈\n"
        "• STAKES Y RETOS 🪜\n"
        "• LOS REYES APP 👑 (CRISTIAN / MARCO / ROBERTO / CONSEJO ABUELO / OSCAR)\n"
        "• JUGADAS EXCLUSIVAS DE $2,000 DE CR Y DINÁMICAS 🤴🏻\n"
        "• GRUPO EXCLUSIVO DE GALLITO VIP + JAPO 🐓\n\n"
        "➡️️ **INCLUIMOS JUGADAS DE PAGA TODOS LOS DÍAS 👏**\n"
        "💎 **COSTO: $250 PESOS (MES DE OCTUBRE)** 💰"
    )
]

# --- SERVIDOR WEB FALSO PARA RENDER (Evita que se apague en el plan gratuito) ---
class DummyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot Ludopata activo 24/7!")

def run_dummy_server():
    server = HTTPServer(('0.0.0.0', 10000), DummyHandler)
    server.serve_forever()

# --- 1. SALUDO Y BIENVENIDA NATURAL ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.effective_user.first_name
    saludo = (
        f"¡Qué tal, mi estimado **{user_name}**! 🎰\n\n"
        "Bienvenido al templo de la buena suerte y las malas decisiones financieras. "
        "¿Vienes por el parlay salvaje de hoy, por la combi matadora o qué nos jugamos?\n\n"
        "Échale un ojo a lo que tenemos activo antes de que la casa nos vuelva a bloquear."
    )
    
    teclado = [
        [InlineKeyboardButton("📊 Ver Promociones y Precios", callback_data="ver_promos")],
        [InlineKeyboardButton("💳 Métodos de Pago", callback_data="ver_pagos")]
    ]
    reply_markup = InlineKeyboardMarkup(teclado)
    
    await update.message.reply_text(saludo, parse_mode="Markdown", reply_markup=reply_markup)

# --- 2. PANEL DE CONTROL EXCLUSIVO PARA EL ADMIN ---
async def cmd_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("Zona prohibida, patrón. Aquí solo manda el dueño.")
        return
    
    teclado = [
        [InlineKeyboardButton("➕ Agregar Promo o Pick Individual", callback_data="admin_agregar_promo")],
        [InlineKeyboardButton("📋 Ver Promos Activas", callback_data="admin_ver_activas")]
    ]
    await update.message.reply_text(
        "🎛️ **PANEL DE CONTROL DEL JEFESITO:**\n\n¿Qué vamos a publicar o modificar hoy?",
        reply_markup=InlineKeyboardMarkup(teclado),
        parse_mode="Markdown"
    )

# --- 3. MANEJADOR DE CLICS DE BOTONES ---
async def botones_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == "ver_promos":
        if not PROMOS_ACTIVAS:
            await query.message.reply_text("Ahorita estamos recargando cartuchos, no hay promos al aire. Pregúntale al Goldenboy.")
            return
        
        texto_promos = "🎟️ **PASES Y PROMOCIONES ACTIVAS:**\n\n"
        for i, promo in enumerate(PROMOS_ACTIVAS, 1):
            texto_promos += f"-----------------------------------\n🔹 **Promo #{i}**\n{promo}\n\n"
        
        texto_promos += "💸 ¿Te late alguna? Mándame un mensaje directo con el comprobante de transferencia y te abro la puerta al Edén."
        await query.message.reply_text(texto_promos, parse_mode="Markdown")
        
    elif query.data == "ver_pagos":
        datos_pago = (
            "🏦 **DATOS PARA CAERLE CON LA LANA:**\n\n"
            "• **Banco:** BBVA\n"
            "• **CLABE:** `012180015465460667`\n"
            "• **CONCEPTO:** 'ASESORIA'\n"
            "• **Titular:** GUILLERMO FUENTES\n\n"
            "• **PAGOS POR PAYPAL (+20 DE COMISIÓN):** `gfueais30@gmail.com`\n\n"
            "⚠️ *Ojo:* En cuanto hagas la transferencia, mándame aquí mismo la foto del comprobante para avisarle al Goldenboy."
        )
        await query.message.reply_text(datos_pago, parse_mode="Markdown")

    elif query.data == "admin_agregar_promo":
        if update.effective_user.id != ADMIN_ID:
            return
        await query.message.reply_text("Para agregar una promo nueva, escribe el comando: `/agregar`", parse_mode="Markdown")

    elif query.data == "admin_ver_activas":
        if update.effective_user.id != ADMIN_ID:
            return
        if not PROMOS_ACTIVAS:
            await query.message.reply_text("📋 No hay ninguna promoción activa en este momento.")
            return
        
        # Te enviamos cada promo con su propio botón para eliminarla individualmente
        for i, promo in enumerate(PROMOS_ACTIVAS):
            teclado_borrar = [[InlineKeyboardButton(f"🗑️ Eliminar Promo #{i+1}", callback_data=f"borrar_{i}")]]
            texto_item = f"📋 **Promo #{i+1}:**\n\n{promo}"
            await query.message.reply_text(texto_item, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(teclado_borrar))

    elif query.data.startswith("borrar_"):
        if update.effective_user.id != ADMIN_ID:
            return
        
        indice = int(query.data.split("_")[1])
        try:
            promo_eliminada = PROMOS_ACTIVAS.pop(indice)
            await query.message.edit_text("🗑️ **¡Promoción eliminada del sistema con éxito!**", parse_mode="Markdown")
        except IndexError:
            await query.message.reply_text("❌ Esa promoción ya había sido eliminada o no existe.")

    elif query.data.startswith("aprobar_"):
        if update.effective_user.id != ADMIN_ID:
            await query.answer("¡Hey! Tú no mandas aquí.", show_alert=True)
            return
        
        cliente_id = int(query.data.split("_")[1])
        
        try:
            await context.bot.send_message(
                chat_id=cliente_id,
                text="✅ ¡Comprobante aprobado por el Goldenboy!\n\nEn un momento te comparto tus accesos de forma manual por este medio. ¡A cobrar se ha dicho! 💰"
            )
            old_caption = query.message.caption or ""
            await query.edit_message_caption(caption=old_caption + "\n\n🟢 **[PAGO APROBADO]**")
        except Exception as e:
            await query.message.reply_text(f"Hubo un error: {e}")

# --- 4. RESPUESTA A TEXTO LIBRE Y COMPROBANTES ---
async def manejar_mensajes_libres(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mensaje = update.message
    user = update.effective_user
    
    if mensaje.photo and user.id != ADMIN_ID:
        foto_file_id = mensaje.photo[-1].file_id
        
        await mensaje.reply_text(
            "¡Vaya, un valiente que sí confía en el proceso! 💸\n\n"
            "Comprobante recibido. Le acabo de chiflar al Goldenboy para que revise si de verdad cayó la lana. En cuanto dé el visto bueno, te mando el acceso."
        )
        
        teclado_admin = [[InlineKeyboardButton("✅ Aprobar Pago", callback_data=f"aprobar_{user.id}")]]
        
        await context.bot.send_photo(
            chat_id=ADMIN_ID,
            photo=foto_file_id,
            caption=f"🚨 **¡NUEVO COMPROBANTE DE PAGO!**\n\n👤 Cliente: {user.full_name} (@{user.username or 'Sin alias'})\n🆔 ID: `{user.id}`",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(teclado_admin)
        )
        return

    if mensaje.text and user.id != ADMIN_ID:
        texto = mensaje.text.lower()
        if any(palabra in texto for palabra in ["hola", "buenos", "info", "precios", "promos", "cuenta"]):
            await mensaje.reply_text(
                "¡Quihubo! ¿Qué se te ofrece, mi estimado? Si vienes por los accesos, escribe /start para ver el menú o mándame de una vez tu captura de pago."
            )

# --- 5. CONVERSACIÓN PARA AGREGAR PROMOS ---
async def cmd_agregar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("Comando exclusivo para el dueño del changarro.")
        return ConversationHandler.END
    
    await update.message.reply_text("A ver, patrón. Escribe el texto completo de la nueva promoción o pick individual que quieres agregar:")
    return PEDIR_INFO_PROMO

async def recibir_nueva_promo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto_promo = update.message.text
    PROMOS_ACTIVAS.append(texto_promo)
    
    await update.message.reply_text("✅ ¡Promo o pick agregado al sistema con éxito y listo para mostrarse a la banda!")
    return ConversationHandler.END

async def cancelar_proceso(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Operación cancelada.")
    return ConversationHandler.END


def main():
    # Arrancamos el servidor web falso en un hilo separado
    server_thread = threading.Thread(target=run_dummy_server, daemon=True)
    server_thread.start()

    app = ApplicationBuilder().token(TOKEN).build()

    conv_promo = ConversationHandler(
        entry_points=[CommandHandler('agregar', cmd_agregar)],
        states={
            PEDIR_INFO_PROMO: [MessageHandler(filters.TEXT & ~filters.COMMAND, recibir_nueva_promo)],
        },
        fallbacks=[CommandHandler('cancelar', cancelar_proceso)],
    )

    app.add_handler(conv_promo)
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("admin", cmd_admin))
    app.add_handler(CallbackQueryHandler(botones_handler))
    app.add_handler(MessageHandler(filters.PHOTO | filters.TEXT, manejar_mensajes_libres))

    print("🤖 Bot ludópata encendido y operando en la nube...")
    
    # Event loop explícito y seguro para Render
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()