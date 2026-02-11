import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton

# Замените на ваш токен от BotFather
TOKEN = "8385299610:AAEyhYL_1dpzWp6_IhIMGKsbqdmW8Jt20IQ"

# Создаем экземпляр бота
bot = telebot.TeleBot(TOKEN)

# Стартовое сообщение
START_MESSAGE = """Добро пожаловать в официальный бот поддержки ФК «Торнадо»!

Здесь вы можете получить помощь по вопросам:
• 📅 Расписание матчей
• 📢 Новости клуба
• ❓ Другие вопросы

Выберите нужный раздел ниже:"""

# Тексты для кнопок
SUPPORT_SECTIONS = {
    "schedule": "📅 Расписание матчей",
    "news": "📢 Новости",
    "contacts": "📞 Контакты",
    "other": "❓ Другой вопрос"
}

# Ответы на разделы
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

# Создаем клавиатуру с кнопками
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

# Обработчик команды /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    keyboard = create_main_keyboard()
    bot.send_message(message.chat.id, START_MESSAGE, 
                     reply_markup=keyboard, 
                     parse_mode='HTML')

# Обработчик текстовых сообщений (нажатия кнопок)
@bot.message_handler(func=lambda message: True)
def handle_buttons(message):
    text = message.text
    
    # Проверяем, какая кнопка была нажата
    for key, button_text in SUPPORT_SECTIONS.items():
        if text == button_text:
            response = SECTION_RESPONSES.get(key, "Раздел в разработке.")
            bot.send_message(message.chat.id, response, parse_mode='HTML')
            return
    
    # Если сообщение не соответствует кнопкам
    bot.send_message(message.chat.id, 
                     "Пожалуйста, используйте кнопки ниже для навигации.",
                     reply_markup=create_main_keyboard())

# Запуск бота
if __name__ == "__main__":
    print("Бот запущен...")
    bot.infinity_polling()

    