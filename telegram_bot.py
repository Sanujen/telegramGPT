import os
import logging
from dotenv import load_dotenv
from telegram import Update, CallbackQuery
from telegram.ext import (
    ContextTypes,
    CommandHandler,
    MessageHandler,
    ApplicationBuilder,
    filters,
    CallbackQueryHandler,
)
from conf import users
from gpt_message_handler import handle_response
from language_handler import (
    get_language_keyboard,
    set_user_language,
    get_user_language,
    translate_text,
)

print("Starting up bot...")
load_dotenv()


TOKEN = os.getenv("TELEGRAM_TOKEN")
BOTNAME = os.getenv("BOTNAME")

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)


def get_message_content(message):
    if message.text:
        return message.text, "text"
    elif message.photo:
        return message.photo[-1].file_id, "photo"
    elif message.document:
        return message.document.file_id, "document"
    elif message.voice:
        return message.voice.file_id, "voice"
    elif message.audio:
        return message.audio.file_id, "audio"
    elif message.video:
        return message.video.file_id, "video"
    else:
        return None, "unknown"


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send language selection keyboard when user starts the bot"""
    await update.message.reply_text(
        "Welcome! Please select your preferred language:",
        reply_markup=get_language_keyboard()
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Try typing anything and I will do my best to respond!"
    )


async def custom_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "This is a custom command, you can add whatever text you want here."
    )


async def restart_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Restarted the bot.")


async def language_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle language selection callback"""
    query: CallbackQuery = update.callback_query
    await query.answer()
    
    # Extract language code from callback data
    lang_code = query.data.split('_')[1]
    user_id = query.from_user.id
    
    # Set user's language preference
    set_user_language(user_id, lang_code)
    
    # Send confirmation in selected language
    if lang_code == 'en':
        await query.message.edit_text("Language set to English!")
    elif lang_code == 'ta':
        await query.message.edit_text("மொழி தமிழுக்கு மாற்றப்பட்டது!")
    elif lang_code == 'si':
        await query.message.edit_text("භාෂාව සිංහලට වෙනස් කරන ලදී!")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.effective_message
    user = update.effective_user
    message_id = message.message_id

    logging.info(f"User {user.username} ({user.id}) sent a message.")

    content, content_type = get_message_content(message)

    if content_type == "unknown":
        await message.reply_text("Sorry, I can't process this type of message yet.")
        return

    if content_type == "text":
        response = await handle_response(content, user, message_id, content_type)
    else:
        # For media files, download the file
        file = await context.bot.get_file(content)
        file_path = await file.download_to_drive()
        # Pass the file path to handle_response
        response = await handle_response(file_path, user, message_id, content_type)

    # Get user's preferred language
    user_lang = get_user_language(user.id)
    
    # Translate response if not in English
    if user_lang != 'en' and isinstance(response, str):
        response = translate_text(response, user_lang)

    if type(response) == str and len(response) > 1000:
        file_name = f"result.md"
        with open(file_name, "w") as file:
            file.write(response)
        await message.reply_document(file_name)

    if type(response) == str:
        await message.reply_markdown(response)
    else:
        await message.reply_markdown(response)


def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    logging.error(msg="Exception while handling an update:", exc_info=context.error)


if __name__ == "__main__":
    application = ApplicationBuilder().token(TOKEN).build()

    # Commands with user restriction
    allowed_users_filter = filters.User(username=users)
    application.add_handler(
        CommandHandler("start", start_command, filters=allowed_users_filter)
    )
    application.add_handler(
        CommandHandler("help", help_command, filters=allowed_users_filter)
    )
    application.add_handler(
        CommandHandler("custom", custom_command, filters=allowed_users_filter)
    )
    application.add_handler(
        CommandHandler("restart", restart_command, filters=allowed_users_filter)
    )
    
    # Add callback handler for language selection
    application.add_handler(CallbackQueryHandler(language_callback, pattern="^lang_"))

    # Message handler with user restriction
    application.add_handler(
        MessageHandler(filters.ALL & allowed_users_filter, handle_message)
    )

    # Error handler
    application.add_error_handler(error_handler)

    application.run_polling()
