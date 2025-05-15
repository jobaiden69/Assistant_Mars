import logging
from telegram import (
    Update,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackContext,
    CallbackQueryHandler,
    ConversationHandler,
    filters
)
import sqlite3
import random
from datetime import datetime

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Константы для состояний ConversationHandler
NAME, AGE, SPECIALIZATION, HEALTH_STATUS = range(4)


# Инициализация базы данных
def init_db():
    conn = sqlite3.connect('mars_colony.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS colonists (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            name TEXT,
            age INTEGER,
            specialization TEXT,
            health_status TEXT,
            registration_date TEXT
        )
    ''')
    conn.commit()
    conn.close()


# Добавление нового колониста
def add_colonist(user_id, name, age, specialization, health_status):
    conn = sqlite3.connect('mars_colony.db')
    cursor = conn.cursor()
    reg_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute(
        'INSERT INTO colonists (user_id, name, age, specialization, health_status, registration_date) VALUES (?, ?, ?, ?, ?, ?)',
        (user_id, name, age, specialization, health_status, reg_date)
    )
    conn.commit()
    conn.close()


# Команда /start
async def start(update: Update, context: CallbackContext) -> None:
    user = update.effective_user
    await update.message.reply_text(
        f"🚀 Добро пожаловать в Марсианскую Колонию, {user.first_name}!\n\n"
        "Я - ваш помощник в освоении Красной Планеты.\n\n"
        "Доступные команды:\n"
        "/help - Список команд\n"
        "/register - Регистрация в базе колонии\n"
        "/select_crew - Выбрать члена экипажа для выхода\n"
        "/morale - Моральная поддержка\n"
        "/check_status - Проверить состояние систем\n"
        "/colonists - Список колонистов"
    )


# Команда /help
async def help_command(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text(
        "🛠 Доступные команды:\n"
        "/help - Список команд\n"
        "/register - Регистрация в базе колонии\n"
        "/select_crew - Выбрать члена экипажа для выхода\n"
        "/morale - Моральная поддержка\n"
        "/check_status - Проверить состояние систем\n"
        "/colonists - Список колонистов"
    )


async def mars_map(update: Update, context: CallbackContext):
    """Отправляет случайную карту Марса"""
    map_types = {
        "Топографическая": "https://astrogeology.usgs.gov/cache/images/04085e995d7c4f4795f61a9c5f3577f3_mars_mola_cylk_lrg.jpg",
        "Минералогическая": "https://planetarymaps.usgs.gov/mosaic/Mars_OMEGA_oxides.jpg",
        "Глобальная": "https://upload.wikimedia.org/wikipedia/commons/0/02/OSIRIS_Mars_true_color.jpg"
    }

    map_name, map_url = random.choice(list(map_types.items()))

    try:
        await update.message.reply_photo(
            photo=map_url,
            caption=f"🗺 {map_name} карта Марса\n\nИспользуйте /map для другой карты"
        )
    except Exception as e:
        logger.error(f"Ошибка при отправке карты: {e}")
        await update.message.reply_text("Не удалось загрузить карту. Попробуйте позже.")


# Команда /morale
async def morale_support(update: Update, context: CallbackContext) -> None:
    """Отправляет мотивационную картинку с котиком для поддержки колонистов"""
    cat_photos = [
        "https://imgur.com/gallery/photo-of-cat-luma-every-day-day-101-wyToWOA"
    ]

    motivational_phrases = [
        "Даже на Марсе есть место для улыбки! 😊",
        "Котики верят в тебя, как и вся Земля! 🌍",
        "Ты делаешь историю! А этот котик - твой фанат!",
        "Расслабься и посмотри на этого котика!",
        "Помни: где-то на Земле котик следит за твоей миссией!"
    ]

    try:
        photo_url = random.choice(cat_photos)
        caption = random.choice(motivational_phrases)
        await update.message.reply_photo(
            photo=photo_url,
            caption=f"🐱 {caption}\n\n#МарсианскаяПоддержка"
        )
    except Exception as e:
        logger.error(f"Ошибка при отправке котика: {e}")
        await update.message.reply_text(
            "🚀 [Изображение недоступно] Помни: ты - первопроходец!\n"
            "Весь Земной шар гордится тобой! 🌎"
        )


# Команда /select_crew
async def select_crew(update: Update, context: CallbackContext) -> None:
    """Выбирает случайного колониста из базы данных для выхода на поверхность"""
    try:
        conn = sqlite3.connect('mars_colony.db')
        cursor = conn.cursor()

        # Получаем всех колонистов с хорошим состоянием здоровья
        cursor.execute('''
            SELECT name, specialization FROM colonists 
            WHERE health_status IN ("Отличное", "Хорошее")
            ORDER BY RANDOM() 
            LIMIT 1
        ''')

        colonist = cursor.fetchone()
        conn.close()

        if colonist:
            name, specialization = colonist
            await update.message.reply_text(
                f"🔴 ВНИМАНИЕ: Система выбрала участника для выхода на поверхность:\n\n"
                f"👉 {name} ({specialization}) 👈\n\n"
                f"Проверьте скафандр и системы жизнеобеспечения!\n"
                f"Рекомендуемая продолжительность выхода: {random.randint(1, 4)} часа"
            )
        else:
            await update.message.reply_text(
                "⚠️ Нет доступных колонистов с подходящим состоянием здоровья.\n"
                "Проверьте /colonists для списка всех членов экипажа."
            )

    except Exception as e:
        logger.error(f"Ошибка при выборе члена экипажа: {e}")
        await update.message.reply_text(
            "🚨 Произошла ошибка при выборе члена экипажа. "
            "Попробуйте позже или проверьте базу данных."
        )


# Команда /colonists
async def list_colonists(update: Update, context: CallbackContext) -> None:
    conn = sqlite3.connect('mars_colony.db')
    cursor = conn.cursor()
    cursor.execute('SELECT name, specialization, health_status FROM colonists')
    colonists = cursor.fetchall()
    conn.close()

    if colonists:
        response = "📋 Список зарегистрированных колонистов:\n\n"
        for colonist in colonists:
            response += f"👤 {colonist[0]} ({colonist[1]}) - {colonist[2]}\n"
        await update.message.reply_text(response)
    else:
        await update.message.reply_text("База данных колонистов пуста.")


# Команда /check_status
async def check_status(update: Update, context: CallbackContext) -> None:
    systems = {
        "Кислород": random.choice(["✅ Норма", "⚠️ Понижен", "❌ Опасность"]),
        "Давление": random.choice(["✅ Норма", "⚠️ Колебания", "❌ Опасность"]),
        "Энергия": random.choice(["✅ Норма", "⚠️ Понижена", "❌ Критично"]),
        "Вода": random.choice(["✅ Норма", "⚠️ Расход", "❌ Дефицит"]),
        "Температура": random.choice(["✅ Норма", "⚠️ Колебания", "❌ Опасность"])
    }

    status_report = "🔧 Статус систем колонии:\n\n"
    for system, state in systems.items():
        status_report += f"{system}: {state}\n"

    await update.message.reply_text(status_report)


# Регистрация - начало
async def register(update: Update, context: CallbackContext) -> int:
    await update.message.reply_text(
        "📝 Регистрация в базе Марсианской Колонии\n\n"
        "Введите ваше полное имя:",
        reply_markup=ReplyKeyboardRemove(),
    )
    return NAME


# Регистрация - имя
async def get_name(update: Update, context: CallbackContext) -> int:
    context.user_data["name"] = update.message.text
    await update.message.reply_text("Сколько вам лет?")
    return AGE


# Регистрация - возраст
async def get_age(update: Update, context: CallbackContext) -> int:
    try:
        age = int(update.message.text)
        if age < 18 or age > 65:
            await update.message.reply_text("Возраст колониста должен быть от 18 до 65 лет.")
            return AGE
        context.user_data["age"] = age

        reply_keyboard = [["Инженер", "Ученый"], ["Медик", "Пилот"], ["Техник", "Другое"]]
        await update.message.reply_text(
            "Выберите вашу специализацию:",
            reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True),
        )
        return SPECIALIZATION
    except ValueError:
        await update.message.reply_text("Пожалуйста, введите корректный возраст.")
        return AGE


# Регистрация - специализация
async def get_specialization(update: Update, context: CallbackContext) -> int:
    context.user_data["specialization"] = update.message.text

    reply_keyboard = [["Отличное", "Хорошее"], ["Удовлетворительное", "Требуется осмотр"]]
    await update.message.reply_text(
        "Оцените ваше текущее состояние здоровья:",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True),
    )
    return HEALTH_STATUS


# Регистрация - здоровье
async def get_health_status(update: Update, context: CallbackContext) -> int:
    health = update.message.text
    user_data = context.user_data

    add_colonist(
        update.effective_user.id,
        user_data["name"],
        user_data["age"],
        user_data["specialization"],
        health
    )

    await update.message.reply_text(
        f"✅ Регистрация завершена, {user_data['name']}!\n\n"
        f"Возраст: {user_data['age']}\n"
        f"Специализация: {user_data['specialization']}\n"
        f"Состояние здоровья: {health}\n\n"
        "Добро пожаловать в Марсианскую Колонию!",
        reply_markup=ReplyKeyboardRemove(),
    )
    return ConversationHandler.END


# Отмена регистрации
async def cancel_registration(update: Update, context: CallbackContext) -> int:
    await update.message.reply_text(
        "Регистрация отменена.",
        reply_markup=ReplyKeyboardRemove(),
    )
    return ConversationHandler.END


# Основная функция
def main() -> None:
    # Инициализация базы данных
    init_db()

    # Создание Application и передача токена бота
    application = Application.builder().token("7601099642:AAGH-IT0xRS_1OwWOntepDk76cxdvvcLVf8").build()

    # Обработчики команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("morale", morale_support))
    application.add_handler(CommandHandler("select_crew", select_crew))
    application.add_handler(CommandHandler("colonists", list_colonists))
    application.add_handler(CommandHandler("check_status", check_status))

    # Обработчик регистрации
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("register", register)],
        states={
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            AGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_age)],
            SPECIALIZATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_specialization)],
            HEALTH_STATUS: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_health_status)],
        },
        fallbacks=[CommandHandler("cancel", cancel_registration)],
    )
    application.add_handler(conv_handler)

    # Запуск бота
    application.run_polling()


if __name__ == '__main__':
    main()