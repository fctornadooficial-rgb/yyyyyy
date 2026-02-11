import os
import sys
import telebot
from flask import Flask, request
from telebot.types import ReplyKeyboardMarkup, KeyboardButton

# ---------- ЛОГИРОВАНИЕ В STDOUT (для Render) ----------
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

# ---------- ТОКЕН ----------
TOKEN = os.environ.get("BOT_TOKEN")
if not TOKEN:
    raise ValueError("❌ Токен не найден! Укажите BOT_TOKEN в переменных окружения.")

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# Проверка токена при старте
try:
    me = bot.get_me()
    logger.info(f"✅ Бот авторизован: @{me.username} (ID: {me.id})")
except Exception as e:
    logger.error(f"❌ Ошибка авторизации бота: {e}")
    raise

# ---------- ВСЕ ВАШИ ДАННЫЕ ----------
START_MESSAGE = """Добро пожаловать в официальный бот поддержки ФК «Торнадо»!

Здесь вы можете получить помощь по вопросам:
• 📅 Расписание матчей
• 📢 Новости клуба
• ❓ Другие вопросы

Выберите нужный раздел ниже:"""

SUPPORT_SECTIONS = {
    "schedule": "📅 Расписание матчей",
    "news": "📢 Новости",
    "contacts": "📞 Контакты",
    "other": "❓ Другой вопрос"
}

SECTION_RESPONSES = {
    "schedule": """<b>Расписание матчей ФК «Торнадо»:</b>

▶ Ближайшие матчи:
пока нет

Полное расписание на сайте: https://fctornadooficial-rgb.github.io/FC-Tornado/""",
    
    "news": """<b>Последние новости клуба:</b>

📰 Все новости: https://fctornadooficial-rgb.github.io/FC-Tornado/

Главные события:
• Разорваны отношения с Ночными Волками""",
    
    "contacts": """<b>Контакты ФК «Торнадо»:</b>

📧 Почта: fctornado.oficial@gmail.com
📍 Адрес стадиона: г. Боровичи, Школа №8

Соцсети:
• Telegram: https://t.me/FCTornado1
• TikToc: @fc.tornado.oficial
• Gmail : fctornado.oficial@gmail.com""",
    
    "other": """<b>Другие вопросы:</b>

Если ваш вопрос не входит в указанные категории, напишите нам:

📩 Написать на почту: fctornado.oficial@gmail.com
💬 Обратиться в Telegram: @YASHI1N

⏱ Время ответа: 1-2 рабочих дня"""
}

def create_main_keyboard():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    buttons = [
        KeyboardButton(SUPPORT_SECTIONS["schedule"]),
        KeyboardButton(SUPPORT_SECTIONS["news"]),
        KeyboardButton(SUPPORT_SECTIONS["contacts"]),
        KeyboardButton(SUPPORT_SECTIONS["other"])
    ]
    keyboard.add(*buttons)
    return keyboard

# ---------- ОБРАБОТЧИКИ КОМАНД С ЗАЩИТОЙ ОТ ОШИБОК ----------
@bot.message_handler(commands=['start'])
def send_welcome(message):
    try:
        logger.info(f"🔥 Команда /start от {message.from_user.id}")
        keyboard = create_main_keyboard()
        bot.send_message(
            message.chat.id,
            START_MESSAGE,
            reply_markup=keyboard,
            parse_mode='HTML'
        )
        logger.info(f"✅ Приветствие отправлено {message.from_user.id}")
    except Exception as e:
        logger.error(f"❌ Ошибка в send_welcome: {e}", exc_info=True)

@bot.message_handler(func=lambda message: True)
def handle_buttons(message):
    try:
        text = message.text
        logger.info(f"💬 Сообщение от {message.from_user.id}: {text}")
        
        for key, button_text in SUPPORT_SECTIONS.items():
            if text == button_text:
                response = SECTION_RESPONSES.get(key, "Раздел в разработке.")
                bot.send_message(message.chat.id, response, parse_mode='HTML')
                logger.info(f"✅ Отправлен ответ на кнопку {key}")
                return
        
        bot.send_message(
            message.chat.id,
            "Пожалуйста, используйте кнопки ниже для навигации.",
            reply_markup=create_main_keyboard()
        )
        logger.info(f"✅ Отправлено напоминание о кнопках")
    except Exception as e:
        logger.error(f"❌ Ошибка в handle_buttons: {e}", exc_info=True)

# ---------- WEBHOOK ----------
@app.route('/', methods=['GET', 'POST', 'HEAD'])
def webhook():
    """Обрабатывает все HTTP-методы, всегда возвращает ответ."""
    if request.method == 'POST':
        try:
            json_str = request.get_data().decode('UTF-8')
            logger.info(f"📦 Webhook POST: {json_str[:200]}...")
            
            update = telebot.types.Update.de_json(json_str)
            bot.process_new_updates([update])
            logger.info("✅ Обновление передано боту")
            
            return 'ok', 200
        except Exception as e:
            logger.error(f"❌ Ошибка webhook: {e}", exc_info=True)
            return 'error', 500
    
    elif request.method == 'HEAD':
        # Render отправляет HEAD-запросы для проверки здоровья
        return '', 200
    
    elif request.method == 'GET':
        return "✅ Бот ФК «Торнадо» работает! Логирование включено.", 200
    
    # На всякий случай
    return 'Method not allowed', 405

@app.route('/setwebhook')
def set_webhook():
    webhook_url = request.url_root.rstrip('/') + '/'
    success = bot.set_webhook(url=webhook_url)
    if success:
        logger.info(f"✅ Вебхук установлен на {webhook_url}")
        return f"✅ Вебхук установлен на {webhook_url}", 200
    else:
        logger.error("❌ Ошибка установки вебхука")
        return "❌ Ошибка установки вебхука", 400

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

