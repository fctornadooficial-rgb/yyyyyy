import os
import sys
import telebot
from flask import Flask, request
from telebot.types import ReplyKeyboardMarkup, KeyboardButton

# ---------- ЛОГИРОВАНИЕ ----------
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

# ---------- ОБРАБОТЧИКИ КОМАНД ----------
@bot.message_handler(commands=['start'])
def send_welcome(message):
    logger.info(f"Получена команда /start от {message.from_user.id}")
    keyboard = create_main_keyboard()
    bot.send_message(
        message.chat.id,
        START_MESSAGE,
        reply_markup=keyboard,
        parse_mode='HTML'
    )
    logger.info(f"Отправлено приветствие пользователю {message.from_user.id}")

@bot.message_handler(func=lambda message: True)
def handle_buttons(message):
    text = message.text
    logger.info(f"Получено сообщение от {message.from_user.id}: {text}")
    
    for key, button_text in SUPPORT_SECTIONS.items():
        if text == button_text:
            response = SECTION_RESPONSES.get(key, "Раздел в разработке.")
            bot.send_message(message.chat.id, response, parse_mode='HTML')
            logger.info(f"Отправлен ответ на кнопку {key}")
            return
    
    bot.send_message(
        message.chat.id,
        "Пожалуйста, используйте кнопки ниже для навигации.",
        reply_markup=create_main_keyboard()
    )
    logger.info(f"Отправлено напоминание о кнопках")

# ---------- WEBHOOK ----------
@app.route('/', methods=['POST', 'GET'])
def webhook():
    if request.method == 'POST':
        try:
            # Читаем JSON из запроса
            json_str = request.get_data().decode('UTF-8')
            logger.info(f"Получен webhook: {json_str[:200]}...")  # первые 200 символов
            
            # Преобразуем в объект Update
            update = telebot.types.Update.de_json(json_str)
            
            # Передаём боту
            bot.process_new_updates([update])
            logger.info("Обновление передано боту")
            
            return 'ok', 200
        except Exception as e:
            logger.error(f"Ошибка при обработке webhook: {e}", exc_info=True)
            return 'error', 500
    elif request.method == 'GET':
        return "✅ Бот ФК «Торнадо» работает! Логирование включено.", 200

@app.route('/setwebhook')
def set_webhook():
    webhook_url = request.url_root.rstrip('/') + '/'
    success = bot.set_webhook(url=webhook_url)
    if success:
        logger.info(f"Вебхук установлен на {webhook_url}")
        return f"✅ Вебхук установлен на {webhook_url}", 200
    else:
        logger.error("Ошибка установки вебхука")
        return "❌ Ошибка установки вебхука", 400

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
