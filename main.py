from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import os
from dotenv import load_dotenv

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Hello. Welcome to Bias Compass, a tool for detecting bias in news articles.\n\nTo begin, simply send the link of an article that you suspect might contain bias.')

def handle_response(text: str) -> str:
    # TODO: 
    # 1. Get article link (do some validation)
    # 2. Run article through compass_v2 logic
    # 3. Return evaluation

    if 'hello' in text:
        return 'Hi there!'

    if 'how are you' in text:
        return 'I\'m good!'

    return 'I don\'t understand'

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_type: str = update.message.chat.type
    text: str = update.message.text

    print(f'User ({update.message.chat.id}) in {message_type}: "{text}"')

    if message_type == 'group':
        if '@BiasCompassBot' in text:
            new_text: str = text.replace('@BiasCompassBot', '').strip()
            response: str = handle_response(new_text)
        else:
            return  # don't respond if not mentioned
    else:
        response: str = handle_response(text)

    await update.message.reply_text(response)

async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f'Update {update} caused error {context.error}')

if __name__ == '__main__':
    load_dotenv()
    app = Application.builder().token(os.environ.get("TELEGRAM_TOKEN")).build()

    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(MessageHandler(filters.TEXT, handle_message))

    app.add_error_handler(error)

    print('Polling...')
    app.run_polling(poll_interval=10)
