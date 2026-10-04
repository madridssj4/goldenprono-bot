import logging
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

# Configuración básica de logs para ver qué pasa en consola
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
PEDIR_TITULO, PEDIR_PRECIO = range(2)

# Memoria temporal para guardar las promociones (se reinicia si apagas el script, 
# luego podemos pasarla a una base de datos si lo requieres)
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
        "➡️ **INCLUIMOS JUGADAS DE PAGA TODOS LOS DÍAS 👏**\n"
        "💎 **COSTO: $250 PESOS (MES DE OCTUBRE)** 💰"
    )
]

# --- 1. SALUDO Y BIENVENIDA NATURAL ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.effective_user.first_name
    saludo = (
        f"¡Qué tal, mi estimado **{user_name}**! 🎰\n\n"
        "Bienvenido al templo de la buena suerte y las malas decisiones financieras. "
        "¿Vienes por el parlay salvaje de hoy, por la combi matadora o qué nos jugamos?\n\n"
        "Échale un ojo a lo que tenemos activo antes de que la casa nos vuelva a bloquear."
    )
    
    # Botones interactivos rápidos
    teclado = [
        [InlineKeyboardButton("📊 Ver Promociones y Precios", callback_data="ver_promos")],
        [InlineKeyboardButton("💳 Métodos de Pago", callback_data="ver_pagos")]
    ]
    reply_markup = InlineKeyboardMarkup(teclado)
    
    await update.message.reply_text(saludo, parse_mode="Markdown", reply_markup=reply_markup)

# --- 2. MANEJADOR DE CLICS DE BOTONES ---
async def botones_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == "ver_promos":
        if not PROMOS_ACTIVAS:
            await query.message.reply_text("Ahorita estamos recargando cartuchos, no hay promos al aire. Pregúntale al Goldenboy.")
            return
        
        texto_promos = "🎟️ **PASES Y PROMOCIONES ACTIVAS:**\n\n"
        for i, promo in enumerate(PROMOS_ACTIVAS, 1):
            texto_promos += f"-----------------------------------\n{promo}\n\n"
        
        texto_promos += "💸 ¿Chingón, no? Mándame un mensaje directo con el comprobante de transferencia y te abro la puerta a la fortuna."
        await query.message.reply_text(texto_promos, parse_mode="Markdown")
        
    elif query.data == "ver_pagos":
        datos_pago = (
            "🏦 **DATOS PARA LO QUE IMPORTA:**\n\n"
            "• **Banco:** BBVA\n"
            "• **CLABE:** `012180015465460667`\n"
            "• **CONCEPTO:** 'ASESORIA'\n"
            "• **Titular:** GUILLERMO FUENTES\n\n"
            "• **PAGOS POR PAYPAL (+20 DE COMISIÓN):** `gfueais30@gmail.com`\n\n"
            "⚠️ *Ojo:* En cuanto hagas la transferencia, mándame aquí mismo la foto del comprobante para avisarle al Goldenboy."
        )
        await query.message.reply_text(datos_pago, parse_mode="Markdown")

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
            await query.edit_message_caption(caption=query.message.caption + "\n\n🟢 **[PAGO APROBADO]**")
        except Exception as e:
            await query.message.reply_text(f"Hubo un error: {e}")

# --- 3. RESPUESTA A TEXTO LIBRE Y COMPROBANTES ---
async def manejar_mensajes_libres(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mensaje = update.message
    user = update.effective_user
    
    # Si mandan una FOTO (Asumimos que es el comprobante de pago)
    if mensaje.photo and user.id != ADMIN_ID:
        foto_file_id = mensaje.photo[-1].file_id
        
        # Le respondemos al cliente para calmar su ansiedad lúdica
        await mensaje.reply_text(
            "¡Vaya, un valiente que sí confía en el proceso! 💸\n\n"
            "Comprobante recibido. Le acabo de chiflar al Goldenboy para que revise si de verdad cayó la lana o si me mandaste un recibo de la luz. En cuanto dé el visto bueno, te paso la llave."
        )
        
        # Notificamos al ADMIN (tú) en privado con un botón para aprobar al instante
        teclado_admin = [[InlineKeyboardButton("✅ Aprobar y Dar Acceso", callback_data=f"aprobar_{user.id}")]]
        
        await context.bot.send_photo(
            chat_id=ADMIN_ID,
            photo=foto_file_id,
            caption=f"🚨 **¡NUEVO COMPROBANTE DE PAGO!**\n\n👤 Cliente: {user.full_name} (@{user.username or 'Sin alias'})\n🆔 ID: `{user.id}`",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(teclado_admin)
        )
        return

    # Si escriben texto normal conversacional
    if mensaje.text and user.id != ADMIN_ID:
        texto = mensaje.text.lower()
        if any(palabra in texto for palabra in ["hola", "buenos", "info", "precios", "promos", "cuenta"]):
            await mensaje.reply_text(
                "¡Quihubo! ¿Qué se te ofrece, mi estimado? Si vienes por los accesos, escribe /start para ver el menú o mándame de una vez tu captura de pago."
            )

# --- 4. PANEL DE ADMINISTRACIÓN: AGREGAR PROMOS DESDE EL MÓVIL ---
async def cmd_agregar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("Comando exclusivo para el dueño del changarro.")
        return ConversationHandler.END
    
    await update.message.reply_text("A ver, patrón. ¿Cómo se va a llamar la nueva promoción o pase?")
    return PEDIR_TITULO

async def recibir_titulo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['nuevo_titulo'] = update.message.text
    await update.message.reply_text("Perfecto. Ahora dime el **precio** (ej. $300 MXN):")
    return PEDIR_PRECIO

async def recibir_precio_promo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    precio = update.message.text
    titulo = context.user_data['nuevo_titulo']
    
    PROMOS_ACTIVAS.append({"titulo": titulo, "precio": precio})
    
    await update.message.reply_text(
        f"✅ ¡Promo agregada al sistema con éxito!\n\n📌 **{titulo}** — **{precio}**\n\nYa está visible para los clientes cuando le piquen a ver promos."
    )
    return ConversationHandler.END

async def cancelar_proceso(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Operación cancelada. Nos fuimos a descanso.")
    return ConversationHandler.END


def main():
    app = ApplicationBuilder().token(TOKEN).build()

    # Manejador conversacional para que el Admin agregue promos paso a paso desde el cel
    conv_promo = ConversationHandler(
        entry_points=[CommandHandler('agregar', cmd_agregar)],
        states={
            PEDIR_TITULO: [MessageHandler(filters.TEXT & ~filters.COMMAND, recibir_titulo)],
            PEDIR_PRECIO: [MessageHandler(filters.TEXT & ~filters.COMMAND, recibir_precio_promo)],
        },
        fallbacks=[CommandHandler('cancelar', cancelar_proceso)],
    )

    app.add_handler(conv_promo)
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(botones_handler))
    app.add_handler(MessageHandler(filters.PHOTO | filters.TEXT, manejar_mensajes_libres))

    print("🤖 Bot ludópata encendido y operando...")
    app.run_polling()

if __name__ == "__main__":
    main()