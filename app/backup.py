from telethon import TelegramClient, events, Button
from telethon.tl.types import PeerChat, PeerChannel, PeerUser
from app.config import config
from app.logger import logger
import google.generativeai as genai
import json
from pydantic import BaseModel
from app.static_values import WELCOME_MSG

API_ID = config["API_ID"]
API_HASH = config["API_HASH"]
PHONE = config["PHONE"]
BOT_API_TOKEN = config["BOT_API_TOKEN"]
GOOGLE_API_KEY = config["GOOGLE_API_KEY"]

class Expense(BaseModel):
    name: str
    amount: int

genai.configure(api_key=GOOGLE_API_KEY)
generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 8192,
    "response_mime_type": "application/json",
    "response_schema": list[Expense]
}

model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=generation_config,
)

chat_session = model.start_chat(
    history=[]
)

# Create a bot client
bot_client = TelegramClient('bot_session', API_ID, API_HASH)

# Create a user client for fetching past messages
user_client = TelegramClient('user_session', API_ID, API_HASH)

# Total Expense is diplayed 
async def fetch_past_messages(chat_id, bot_id, event: events.NewMessage.Event):
    logger.info(f"Fetching past messages for chat ID: {chat_id}")
    
    chats = ""
    async for message in user_client.iter_messages(chat_id):
        if isinstance(message.from_id, PeerUser):
            if not message.from_id.user_id == bot_id:
                if message.text:
                    chats += "\n" + message.text
    prompt = f"List Expenses from the chats: '{chats}'"
    response = chat_session.send_message(prompt)
    response_text = response.text.strip() 
    expenses = json.loads(response_text)
    total = 0
    results = []
    for item in expenses:
        results.append(f"{item['name']}: {item['amount']}")
        total += item["amount"]
    results.append(f"Total: {total}")
    expense_str = ", ".join(results[:-1]) 
    settlements = split_payments(expense_str)

    return results, settlements

# Equally split the Expense among the given members
def split_payments(payment_str):
    payments = {}
    payment_entries = payment_str.split(",")
    
    for entry in payment_entries:
        name, amount = entry.strip().split(":")
        payments[name.strip()] = float(amount.strip())

    people = list(payments.keys())
    values_paid = list(payments.values())

    total_sum = sum(values_paid)
    mean = total_sum / len(people)

    sorted_people = sorted(people, key=lambda person: payments[person])
    sorted_values_paid = [payments[person] - mean for person in sorted_people]

    i = 0
    j = len(sorted_people) - 1
    settlements = []

    while i < j:
        debt = min(-sorted_values_paid[i], sorted_values_paid[j])
        sorted_values_paid[i] += debt
        sorted_values_paid[j] -= debt

        settlement = f"{sorted_people[i]} will give {sorted_people[j]}: {debt:.2f}"
        settlements.append(settlement)

        if sorted_values_paid[i] == 0:
            i += 1
        if sorted_values_paid[j] == 0:
            j -= 1

    return settlements

# When message is triggered Welcome message will be passed
@bot_client.on(events.NewMessage(incoming=True, forwards=False, pattern=r'/help'))
async def event_handler(event: events.NewMessage.Event):
    
    chat_id = event.message.peer_id
    # Check if the message is from a group chat or channel
    if isinstance(chat_id, (PeerChat, PeerChannel)):
        logger.info(f"Message from group or channel: {chat_id}")
        markup = bot_client.build_reply_markup([Button.inline('Expense', b'Expense'), Button.inline('Split', b'Split')])
        await bot_client.send_message(event.chat_id, WELCOME_MSG, buttons=markup)
    else:
        logger.info(f"Message from a private chat with user: {event.chat_id}")
        await bot_client.send_message(event.chat_id, "Hello user!")


# /expense - Calculate the total expenses.
@bot_client.on(events.NewMessage(incoming=True, forwards=False, pattern=r'/expense'))
async def expense_command_handler(event: events.NewMessage.Event):
    chat_id = event.chat_id
    bot = await bot_client.get_me()
    if isinstance(event.peer_id, (PeerChat, PeerChannel)):
       
        results, settlements = await fetch_past_messages(chat_id, bot.id, event)
        await bot_client.send_message(chat_id, "\n".join(results))
    else:
        logger.info(f"Message from a private chat with user: {event.chat_id}")
        await bot_client.send_message(event.chat_id, "Hello user!")

# /split – Divide the total expense among the names.
@bot_client.on(events.NewMessage(incoming=True, forwards=False, pattern=r'/split'))
async def split_command_handler(event: events.NewMessage.Event):
    chat_id = event.chat_id
    bot = await bot_client.get_me()
    if isinstance(event.peer_id, (PeerChat, PeerChannel)):

        results, settlements = await fetch_past_messages(chat_id, bot.id, event)
        await bot_client.send_message(chat_id, "\n".join(settlements))
    else:
        logger.info(f"Message from a private chat with user: {event.chat_id}")
        await bot_client.send_message(event.chat_id, "Hello user!")


# Once the user or bot itself is added the welcome message will be passed
@bot_client.on(events.ChatAction)
async def chat_action_handler(event: events.ChatAction.Event):
    chat_id = event.chat_id
    if event.user_added or event.user_joined:
        logger.info(f"User joined group or was added: {chat_id}")
        markup = bot_client.build_reply_markup([Button.inline('Expense', b'Expense'), Button.inline('Split', b'Split')])
        await bot_client.send_message(event.chat_id, WELCOME_MSG, buttons=markup)
    elif event.user_added and event.user_id == (await bot_client.get_me()).id:
        logger.info(f"Bot added to group: {chat_id}")
        markup = bot_client.build_reply_markup([Button.inline('Expense', b'Expense'), Button.inline('Split', b'Split')])
        await bot_client.send_message(event.chat_id, WELCOME_MSG, buttons=markup)



# Handle button clicks
@bot_client.on(events.CallbackQuery)
async def callback_handler(event: events.CallbackQuery.Event):
    chat_id = event.chat_id
    bot = await bot_client.get_me()
    await event.answer('Please wait until processing is done...')
    results, settlements = await fetch_past_messages(chat_id, bot.id, event)
    data = event.data.decode("utf-8")
    if data == "Expense":
        await bot_client.send_message(event.chat_id, "\n".join(results))
    elif data == "Split":
        await bot_client.send_message(event.chat_id, "\n".join(settlements))

# Function to start the user client for past messages
async def start_user_client():
    try:
        await user_client.start(phone=PHONE)
        logger.info("User client started successfully.")
    except Exception as e:
        logger.error(f"User client failed to start: {e}")

try:
    # Start the bot client using the bot token
    bot_client.start(bot_token=BOT_API_TOKEN)
    logger.info("Bot client started successfully.")
    
    # Start the user client separately
    bot_client.loop.run_until_complete(start_user_client())
    
    # Run both clients
    bot_client.run_until_disconnected()
except Exception as e:
    logger.error(f"Exception: {e}")
