from typing import Final
from datetime import datetime
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes, CommandHandler
import nse_get_data

TOKEN: Final = "8255069137:AAHPwP4dXQr3aOxAZiMKVWRhT0a4H_z_daM"
CHAT_ID: Final = "-4874857541"
BOT_USERNAME: Final = "@vcautomationbot"

# Commands
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello! I'm your automation bot. How can I assist you today?")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "Here are the commands you can use:\n"
        "/start - Start the bot\n"
        "/help - Show this help message\n"
        "You can also send any text message, and I'll respond with the current status."
    )
    await update.message.reply_text(help_text)

async def custom_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # This is where you can implement any custom command logic
    await update.message.reply_text("This is a custom command response!")

#Responses
def is_date_string(text: str) -> bool:
    try:
        datetime.strptime(text.strip(), "%d-%m-%Y")
        return True
    except ValueError:
        return False


def handle_response(text: str) -> str:
    # Implement your logic to generate a response based on the input text
    if "status" in text.lower():
        return "The current status is: All systems operational."
    elif "temperature" in text.lower():
        return "The current temperature is 25°C."
    elif is_date_string(text):
        return nse_get_data.pretty_table_from_text(nse_get_data.get_market_summary_nseLandG(text))
    else:
        return "Sorry, I didn't understand that. Please try again."

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_type: str = update.message.chat.type
    text: str = update.message.text
    print(f'User ({update.message.from_user.username}) sent a message in {message_type} chat: {text}')

    if message_type == "group":
        if BOT_USERNAME in text:
            new_text: str = text.replace(BOT_USERNAME, "").strip()
            response:str = handle_response(new_text)
        else:
            return
    else:
        response = handle_response(text)
    
    # print(f"Bot: {response}") #Uncomment for debugging
    await update.message.reply_text(response)

async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f"Update {update} caused an error: {context.error}")

if __name__ == "__main__":
    print("Starting the bot...")
    app = Application.builder().token(TOKEN).build()

    # Add command handlers
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("custom", custom_command))

    # Add a handler for all text messages
    app.add_handler(MessageHandler(filters.TEXT, handle_message))

    # Add error handler
    app.add_error_handler(error)

    print("Bot is polling...")
    app.run_polling(poll_interval=1)