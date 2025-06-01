from deep_translator import GoogleTranslator
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

# Language codes
LANGUAGES = {
    'English': 'en',
    'Tamil': 'ta',
    'Sinhala': 'si'
}

# Store user language preferences
user_languages = {}

def get_language_keyboard():
    """Create inline keyboard for language selection"""
    keyboard = [
        [
            InlineKeyboardButton("English", callback_data="lang_en"),
            InlineKeyboardButton("Tamil", callback_data="lang_ta"),
            InlineKeyboardButton("Sinhala", callback_data="lang_si")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

def set_user_language(user_id: int, language_code: str):
    """Set the language preference for a user"""
    user_languages[user_id] = language_code

def get_user_language(user_id: int) -> str:
    """Get the language preference for a user"""
    return user_languages.get(user_id, 'en')  # Default to English

def translate_text(text: str, target_lang: str) -> str:
    """Translate text to target language"""
    try:
        translator = GoogleTranslator(source='auto', target=target_lang)
        translation = translator.translate(text)
        return translation
    except Exception as e:
        print(f"Translation error: {e}")
        return text  # Return original text if translation fails 