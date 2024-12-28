import os
import asyncio
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, Router
from aiogram.types import Message
from aiogram.filters import CommandStart, Command
import google.generativeai as genai

# Load environment variables
load_dotenv()

# Get API keys from environment
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Configure Gemini API
genai.configure(api_key=GEMINI_API_KEY)

# Initialize conversation history
conversation_history = []

# Initialize router
router = Router()

# Function to clear conversation history
def clear_history():
    global conversation_history
    conversation_history.clear()

# Start and help command handler
@router.message(CommandStart())
async def start_help(message: Message):
    help_text = """
    Hi there! I'm your friendly Telegram bot. Here's what I can do:
    - Send me a text message, and I'll provide a response.
    - Use /clear to start a new conversation.
    """
    await message.reply(help_text)

# Clear command handler
@router.message(Command("clear"))
async def clear_command(message: Message):
    clear_history()
    await message.reply("Conversation history cleared.")

# Message handler
@router.message()
async def handle_message(message: Message):
    global conversation_history
    
    # Add user message to conversation history
    conversation_history.append({"role": "user", "parts": [message.text]})

    try:
        # Initialize model (use the appropriate model)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Start chat session
        chat = model.start_chat(history=conversation_history)
        
        # Generate response
        response = chat.send_message(message.text)
        
        # Add assistant response to conversation history
        conversation_history.append({"role": "model", "parts": [response.text]})
        
        # Reply to the user
        await message.reply(response.text)
    
    except Exception as e:
        await message.reply(f"An error occurred: {str(e)}")

# Main function to set up and run the bot
async def main():
    # Initialize bot and dispatcher
    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    dp = Dispatcher()
    
    # Add router to dispatcher
    dp.include_router(router)
    
    # Start polling
    try:
        await dp.start_polling(bot, skip_updates=False)
    except Exception as e:
        print(f"An error occurred while starting the bot: {e}")
    finally:
        await bot.session.close()

# Run the bot
if __name__ == '__main__':
    asyncio.run(main())