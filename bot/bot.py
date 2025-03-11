from telegram import ReplyKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import random
import time
import re

# Токен вашего бота
TOKEN = ""

# Список администраторов 
ADMINS = []

# Ограничение на количество сообщений и время ожидания
MESSAGE_LIMIT = 15  # Увеличили лимит сообщений
WAIT_TIME = 600  # 10 минут в секундах

# Словари для хранения данных
user_message_counts = {}  # Количество сообщений для каждого пользователя
user_wait_times = {}  # Время ожидания для каждого пользователя
user_needs_login = {}  # Нужен ли логин от пользователя
user_language = {}  # Язык пользователя
user_data = {}  # Данные пользователей (для ответов администратора)

LOGIN_FILE = "login.txt"  # Файл, где хранятся логины

# Вариации текста для подтверждения запроса
confirmation_texts_ru = [
    "Мы получили твой запрос и уже работаем над ним. Оставайся на связи! 😊",
    "Твой запрос успешно зарегистрирован. Мы скоро свяжемся с тобой! 📨",
    "Спасибо за обращение! Мы приняли твой запрос и скоро дадим ответ. ⏳",
    "Мы получили твое сообщение и обязательно поможем тебе. Будь на связи! 🤝",
    "Твой запрос принят и находится в обработке. Пожалуйста, ожидай ответа. 🕒"
]

confirmation_texts_en = [
    "We have received your request and are already working on it. Stay tuned! 😊",
    "Your request has been successfully registered. We will contact you soon! 📨",
    "Thank you for contacting us! We have received your request and will respond soon. ⏳",
    "We have received your message and will definitely help you. Stay tuned! 🤝",
    "Your request has been accepted and is being processed. Please wait for a response. 🕒"
]

# Варианты ответов для кнопки "Start"
start_responses_ru = [
    "🌟 Рад видеть тебя здесь. Что случилось? 😊",
    "🎉 Ты попал в нужное место. Спроси меня о чем угодно! 🚀"
]

start_responses_en = [
    "🌟 Glad to see you here. What happened? 😊",
    "🎉 You've come to the right place. Ask me anything! 🚀"
]

# Варианты ответов для кнопки "Question"
question_responses_ru = [
    "Чем могу тебе помочь? 🤔 Расскажи все, и я постараюсь найти ответ!",
    "Спрашивай, не стесняйся! Я здесь, чтобы помочь тебе. 😊",
    "Что тебя интересует? 🕵️ Задай вопрос, и я сделаю все возможное!",
    "Готов ответить на любой твой вопрос! 🎯 Что тебя волнует?",
    "Задавай вопрос, а я постараюсь найти решение! 🧩",
    "Я весь внимание! 👂 Расскажи, что тебе нужно?",
    "Спрашивай смело! Я здесь, чтобы помочь тебе разобраться. 🤗",
    "Что бы ты ни спросил, я постараюсь помочь! 🎓",
    "Задавай вопрос, и мы найдем ответ вместе! 🚀",
    "Я готов помочь! 🎯 Что тебя интересует?"
]

question_responses_en = [
    "How can I help you? 🤔 Tell me everything and I will try to find an answer!",
    "Ask, don't hesitate! I'm here to help you. 😊",
    "What are you interested in? 🕵️ Ask a question and I will do my best!",
    "Ready to answer any of your questions! 🎯 What's bothering you?",
    "Ask a question and I will try to find a solution! 🧩",
    "I'm all ears! 👂 Tell me what you need?",
    "Ask boldly! I'm here to help you figure it out. 🤗",
    "Whatever you ask, I will try to help! 🎓",
    "Ask a question and we will find the answer together! 🚀",
    "I'm ready to help! 🎯 What are you interested in?"
]

# Варианты ответов для кнопки "Idea"
idea_responses_ru = [
    "Ого, ты пришел с идеей! 🚀 Мы тебя слушаем! Возможно, именно твое предложение станет следующим большим шагом вперед! 💡",
    "Идеи? Это здорово! 💡 Делись, мы всегда открыты для нового!",
    "У тебя есть идея? 🔥 Мы готовы выслушать и, возможно, воплотить ее в жизнь!",
    "Идеи — это топливо прогресса! ⛽ Делись, что у тебя на уме!",
    "О, идея? Это круто! 🎯 Мы всегда рады новым предложениям!",
    "Идеи — это то, что движет миром! 🌍 Расскажи, что ты придумал!",
    "Твоя идея может изменить всё! 🚀 Делись, мы слушаем!",
    "Идеи? Это то, что нам нужно! 💡 Дай волю своему воображению!",
    "Мы всегда рады новым идеям! 🎉 Что ты придумал?",
    "Идеи — это суперсила! 🦸 Делись, и мы поможем их реализовать!"
]

idea_responses_en = [
    "Wow, you came up with an idea! 🚀 We are listening to you! Perhaps your proposal will be the next big step forward! 💡",
    "Ideas? That's great! 💡 Share, we are always open to new things!",
    "Do you have an idea? 🔥 We are ready to listen and possibly bring it to life!",
    "Ideas are the fuel of progress! ⛽ Share what's on your mind!",
    "Oh, an idea? That's cool! 🎯 We are always happy to hear new suggestions!",
    "Ideas are what drive the world! 🌍 Tell us what you came up with!",
    "Your idea can change everything! 🚀 Share, we're listening!",
    "Ideas? That's what we need! 💡 Give free rein to your imagination!",
    "We are always happy to hear new ideas! 🎉 What did you come up with?",
    "Ideas are a superpower! 🦸 Share and we will help you implement them!"
]

# Варианты ответов для кнопки "Problem"
problem_responses_ru = [
    "Ох, кажется, у тебя проблема? 😯 Не переживай, мы поможем! Пожалуйста, отправь свой логин:",
    "Проблема? Не беда! 🛠 Отправь свой логин, и мы начнем решать ее вместе.",
    "Кажется, у тебя возникли сложности? 😕 Отправь свой логин, и мы обязательно поможем!",
    "Проблемы — это временно! ⏳ Отправь свой логин, и мы найдем решение.",
    "Не переживай, мы справимся! 🎯 Отправь свой логин, чтобы мы могли помочь.",
    "Проблема? Мы уже в пути! 🚑 Отправь свой логин, и мы начнем работу.",
    "Сложности? Не беда! 🛠 Отправь свой логин, и мы разберемся.",
    "Мы здесь, чтобы помочь! 🎯 Отправь свой логин, и мы начнем решать твою проблему.",
    "Проблемы — это вызовы, которые мы преодолеваем вместе! 🤝 Отправь свой логин.",
    "Не переживай, мы уже работаем над решением! 🛠 Отправь свой логин."
]

problem_responses_en = [
    "Oh, looks like you have a problem? 😯 Don't worry, we'll help! Please send your login:",
    "Problem? No problem! 🛠 Send your login and we will start solving it together.",
    "Looks like you're having difficulties? 😕 Send your login and we will definitely help!",
    "Problems are temporary! ⏳ Send your login and we will find a solution.",
    "Don't worry, we'll handle it! 🎯 Send your login so we can help.",
    "Problem? We are already on our way! 🚑 Send your login and we will start working.",
    "Difficulties? No problem! 🛠 Send your login and we will figure it out.",
    "We are here to help! 🎯 Send your login and we will start solving your problem.",
    "Problems are challenges that we overcome together! 🤝 Send your login.",
    "Don't worry, we are already working on a solution! 🛠 Send your login."
]

# Варианты ответов для кнопки "Stop"
stop_texts_ru = [
    "Хорошо, обращайся, если что-то еще понадобится! Просто напиши /start, чтобы начать заново. 😊",
    "Понял, если возникнут вопросы, не стесняйся начать новый сеанс с помощью /start. 👍",
    "Принято. Если тебе снова понадобится помощь, просто введи /start. 🤝",
    "Окей. Буду ждать твоего возвращения! Напиши /start, когда будешь готов. ⏳",
    "Всегда рад помочь! Если что-то изменится, напиши /start. 😄"
]

stop_texts_en = [
    "Okay, feel free to contact me if you need anything else! Just type /start to start over. 😊",
    "Got it, if you have any questions, feel free to start a new session using /start. 👍",
    "Accepted. If you need help again, just enter /start. 🤝",
    "Okay. I'll be waiting for your return! Type /start when you're ready. ⏳",
    "Always happy to help! If anything changes, type /start. 😄"
]

# Функция для проверки логина в файле
def check_login_in_file(login, filename=LOGIN_FILE):
    try:
        with open(filename, 'r') as file:
            logins = [line.strip() for line in file]  # Читаем все логины в список
            return login in logins  # Проверяем наличие логина в списке
    except FileNotFoundError:
        print(f"Файл {filename} не найден.")
        return False

# Функция для выбора текста в зависимости от языка
def get_localized_text(user_id, texts_ru, texts_en):
    if user_id in user_language and user_language[user_id] == 'en':
        return random.choice(texts_en)
    else:
        return random.choice(texts_ru)

# Функция для команды /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_message_counts[user_id] = 0  # Инициализируем счетчик сообщений при старте
    user_wait_times[user_id] = 0  # Инициализируем время ожидания
    user_needs_login[user_id] = False  # Изначально не запрашиваем логин

    # Создаем клавиатуру с кнопками выбора языка
    keyboard = [['🇷🇺 Русский', '🇬🇧 English']]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text("Выберите язык / Choose a language:", reply_markup=reply_markup)

# Функция для установки языка
async def set_language(update: Update, context: ContextTypes.DEFAULT_TYPE, language: str):
    user_id = update.effective_user.id
    user_language[user_id] = language

    # Выбираем приветствие в зависимости от языка
    if language == 'en':
        welcome_message = (
            "Hello! 👋 I am your assistant and I am here to make your experience with the application as convenient and enjoyable as possible! 😊\n\n"
            "Here's what I can do for you:\n\n"
            "🌟 **Start** — Click this button if you want to start a conversation with me! I am always ready to help you with questions, give advice, or just chat. Let's get started! 🚀\n\n"
            "❓ **Question** — If you have any questions about our application, feel free to click here! I will try to answer as quickly and clearly as possible. Don't hesitate to ask! 🤔\n\n"
            "🔑 **Problem** — Forgot your login? No problem! Click this button and I will help you restore access to your account. Together we can handle it! 💪\n\n"
            "💡 **Idea** — Do you have an idea how to improve our application? Click here and share your thoughts! Perhaps your proposal will be the impetus for new improvements! 🚀\n\n"
            "🛑 **Stop** — If you need to stop the bot, just click this button. Your request will be accepted and I will contact you within 24 hours. I promise! ⏳\n\n"
            "Feel free to choose the button you need — I'm always here to help! 😄 Let's make your application experience even better! 🚀"
        )
        keyboard = [['🌟 Start', '❓ Question'], ['💡 Idea', '🔑 Problem'], ['🛑 Stop']]
    else:  # Русский язык
        welcome_message = (
            "Привет! 👋 Я твой помощник, и я здесь, чтобы сделать твое общение с приложением максимально удобным и приятным! 😊\n\n"
            "Вот что я могу для тебя сделать:\n\n"
            "🌟 **Start** — Нажми эту кнопку, если хочешь начать общение со мной! Я всегда готов помочь тебе с вопросами, дать совет или просто поболтать. Давай начнем! 🚀\n\n"
            "❓ **Question** — Если у тебя есть любой вопрос о нашем приложении, смело жми сюда! Я постараюсь ответить максимально быстро и понятно. Не стесняйся спрашивать! 🤔\n\n"
            "🔑 **Problem** — Забыл логин? Не беда! Нажми эту кнопку, и я помогу тебе восстановить доступ к аккаунту. Вместе мы справимся! 💪\n\n"
            "💡 **Idea** — Есть идея, как улучшить наше приложение? Нажми сюда и поделись своими мыслями! Возможно, именно твое предложение станет толчком к новым улучшениям! 🚀\n\n"
            "🛑 **Stop** — Если тебе нужно остановить бота, просто нажми эту кнопку. Твой запрос будет принят, и я свяжусь с тобой в течение 24 часов. Обещаю! ⏳\n\n"
            "Не стесняйся выбирать нужную кнопку — я всегда рядом, чтобы помочь! 😄 Давай сделаем твой опыт использования приложения еще лучше! 🚀"
        )
        keyboard = [['🌟 Start', '❓ Question'], ['💡 Idea', '🔑 Problem'], ['🛑 Stop']]

    # Добавляем кнопку ответа для администраторов
    if user_id in ADMINS:
        keyboard.append(['📨 Reply to User'])

    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(welcome_message, reply_markup=reply_markup)

# Функция для обработки текстовых сообщений (нажатий кнопок)
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    current_time = time.time()
    text = update.message.text

    # Пересылаем сообщение администратору с указанием ID пользователя
    if user_id not in ADMINS:  # Чтобы не пересылать сообщения самого администратора
        for admin_id in ADMINS:
            # Формируем сообщение с ID пользователя и его текстом
            admin_message = (
                f"Сообщение от пользователя:\n"
                f"ID: <code>{user_id}</code>\n"
                f"Текст: {text}"
            )
            await context.bot.send_message(
                chat_id=admin_id, 
                text=admin_message,
                parse_mode='HTML'
            )
            user_data[user_id] = {"last_message": text}  # Сохраняем последнее сообщение пользователя

    # Проверяем выбор языка
    if text == '🇷🇺 Русский':
        await set_language(update, context, 'ru')
        return
    elif text == '🇬🇧 English':
        await set_language(update, context, 'en')
        return

    # Проверяем необходимость ввода логина
    if user_needs_login.get(user_id):
        if re.match(r'^[a-zA-Z0-9]+$', text):
            login = text.strip()
            if check_login_in_file(login):
                # Используем текст в зависимости от языка
                if user_id in user_language and user_language[user_id] == 'en':
                    await update.message.reply_text(
                        "Login found! Now wait a little and stay in touch. We have accepted your request! We will contact you within 24 hours. ✅")
                else:
                    await update.message.reply_text(
                        "Логин найден! Теперь немного подожди и будь на связи. Мы приняли твой запрос! Свяжемся с тобой в течение 24 часов. ✅")
            else:
                # Используем текст в зависимости от языка
                if user_id in user_language and user_language[user_id] == 'en':
                    await update.message.reply_text("Unfortunately, we did not find such a login in our database. 😔")
                else:
                    await update.message.reply_text("Увы, мы не нашли такой логин в нашей базе данных. 😔")
            user_needs_login[user_id] = False  # Снимаем флаг запроса логина
            return
        else:
            # Используем текст в зависимости от языка
            if user_id in user_language and user_language[user_id] == 'en':
                await update.message.reply_text("Please enter only your login (letters and numbers). 🔤")
            else:
                await update.message.reply_text("Пожалуйста, введите только ваш логин (буквы и цифры). 🔤")
            return

    # Проверяем режим ожидания пользователя
    if user_id in user_wait_times and user_wait_times[user_id] > current_time:
        remaining_time = int(user_wait_times[user_id] - current_time)
        # Используем текст в зависимости от языка
        if user_id in user_language and user_language[user_id] == 'en':
            await update.message.reply_text(f"Please wait {remaining_time // 60} minutes {remaining_time % 60} seconds. ⏳")
        else:
            await update.message.reply_text(f"Пожалуйста, подождите {remaining_time // 60} минут {remaining_time % 60} секунд. ⏳")
        return

    # Инкрементируем счетчик сообщений для пользователя
    if user_id not in user_message_counts:
        user_message_counts[user_id] = 0
    user_message_counts[user_id] += 1

    # Проверяем лимит сообщений
    if user_message_counts[user_id] > MESSAGE_LIMIT:
        user_wait_times[user_id] = current_time + WAIT_TIME
        user_message_counts[user_id] = 0  # Сбрасываем счетчик
        # Используем текст в зависимости от языка
        if user_id in user_language and user_language[user_id] == 'en':
            await update.message.reply_text("You have reached the message limit. Please wait 10 minutes. ⏳")
        else:
            await update.message.reply_text("Вы достигли лимита сообщений. Пожалуйста, подождите 10 минут. ⏳")
        return

    # Обработка нажатий кнопок
    if text == '🌟 Start':
        response = get_localized_text(user_id, start_responses_ru, start_responses_en)
        await update.message.reply_text(response)

    elif text == '❓ Question':
        response = get_localized_text(user_id, question_responses_ru, question_responses_en)
        await update.message.reply_text(response)

    elif text == '💡 Idea':
        response = get_localized_text(user_id, idea_responses_ru, idea_responses_en)
        await update.message.reply_text(response)

    elif text == '🔑 Problem':
        user_needs_login[user_id] = True  # Устанавливаем флаг запроса логина
        response = get_localized_text(user_id, problem_responses_ru, problem_responses_en)
        await update.message.reply_text(response)

    elif text == '🛑 Stop':
        response = get_localized_text(user_id, stop_texts_ru, stop_texts_en)
        await update.message.reply_text(response)

    elif text == '📨 Reply to User':
        await reply_to_user(update, context)

# Функция для ответа администратора пользователю
async def reply_to_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    # Проверяем, что команду вызвал администратор
    if user_id in ADMINS:
        try:
            # Проверяем, была ли это кнопка или команда
            if update.message.text == '📨 Reply to User':
                await update.message.reply_text(
                    "Чтобы ответить пользователю, используйте команду:\n"
                    "/reply <ID пользователя> <текст ответа>\n\n"
                    "Пример:\n"
                    "/reply 123456789 Привет, как я могу помочь?"
                )
                return

            # Получаем аргументы команды: /reply <user_id> <текст ответа>
            args = context.args
            if len(args) < 2:
                await update.message.reply_text(
                    "Использование: /reply <user_id> <текст ответа>\n"
                    "Пример: /reply 123456789 Привет, как я могу помочь?"
                )
                return

            target_user_id = int(args[0])  # ID пользователя, которому нужно ответить
            reply_text = " ".join(args[1:])  # Текст ответа

            # Отправляем ответ пользователю
            await context.bot.send_message(chat_id=target_user_id, text=reply_text)
            await update.message.reply_text(f"✅ Ответ отправлен пользователю {target_user_id}")
        except ValueError:
            await update.message.reply_text("❌ Ошибка: Неверный формат ID пользователя. ID должен быть числом.")
        except Exception as e:
            error_message = str(e)
            if "chat not found" in error_message.lower():
                await update.message.reply_text("❌ Ошибка: Пользователь не найден или бот не может отправить ему сообщение.")
            elif "bot was blocked" in error_message.lower():
                await update.message.reply_text("❌ Ошибка: Пользователь заблокировал бота.")
            else:
                await update.message.reply_text(f"❌ Ошибка: {error_message}")
    else:
        await update.message.reply_text("❌ У вас нет прав для выполнения этой команды.")

# Основная функция запуска бота
def main():
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("reply", reply_to_user))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.run_polling()

if __name__ == '__main__':
    main()