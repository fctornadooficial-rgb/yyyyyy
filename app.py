import os
import telebot
from flask import Flask, request
from telebot.types import ReplyKeyboardMarkup, KeyboardButton

# ---------- ТОКЕН БЕЗОПАСНО ----------
# На Render создайте переменную окружения BOT_TOKEN со значением вашего токена
TOKEN = os.environ.get("BOT_TOKEN")
if not TOKEN:
    raise ValueError("❌ Токен не найден! Укажите BOT_TOKEN в переменных окружения.")

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# ---------- ВЕСЬ ВАШ СТАРЫЙ КОД (КОНТЕНТ) ----------
# Всё, что у вас было после создания бота, переносится сюда без изменений

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

@bot.message_handler(commands=['start'])
def send_welcome(message):
    keyboard = create_main_keyboard()
    bot.send_message(message.chat.id, START_MESSAGE,
                     reply_markup=keyboard,
                     parse_mode='HTML')

@bot.message_handler(func=lambda message: True)
def handle_buttons(message):
    text = message.text
    for key, button_text in SUPPORT_SECTIONS.items():
        if text == button_text:
            response = SECTION_RESPONSES.get(key, "Раздел в разработке.")
            bot.send_message(message.chat.id, response, parse_mode='HTML')
            return
    bot.send_message(message.chat.id,
                     "Пожалуйста, используйте кнопки ниже для навигации.",
                     reply_markup=create_main_keyboard())

# ---------- WEBHOOK ----------
@app.route('/', methods=['POST', 'GET'])
def webhook():
    if request.method == 'POST':
        update = telebot.types.Update.de_json(request.stream.read().decode('utf-8'))
        bot.process_new_updates([update])
        return 'ok', 200
    elif request.method == 'GET':
        return "✅ Бот ФК «Торнадо» работает!", 200

# (Опционально) эндпоинт для установки вебхука — можно вызвать 1 раз в браузере
@app.route('/setwebhook')
def set_webhook():
    # Render даст вам URL вида https://название-проекта.onrender.com
    webhook_url = request.url_root.rstrip('/') + '/'
    success = bot.set_webhook(url=webhook_url)
    if success:
        return f"✅ Вебхук установлен на {webhook_url}", 200
    else:
        return "❌ Ошибка установки вебхука", 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
