from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = "8516902152:AAHWbtnl-2TfzTrWxgSTF2oPeCfqAGY5gDI"  # <- сюда твой токен от @BotFather

players = []

# Основное меню
menu = ReplyKeyboardMarkup([
    ["➕ Добавить себя"],
    ["🔎 Найти тиммейтов"],
    ["❌ Удалить анкету"]
], resize_keyboard=True)

# Возможные варианты
servers = [["Европа", "Азия"], ["Америка", "Ближний Восток"]]
modes = [["Классика", "Ранк", "TDM"]]
ranks = [["Bronze", "Silver"], ["Gold", "Platinum"], ["Diamond", "Crown"], ["Ace", "Conqueror"]]
mic_options = [["Да", "Нет"]]

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Добро пожаловать в PUBG Team Finder!", reply_markup=menu)

# Обработка сообщений
async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user = update.message.from_user

    global players

    # ➕ Добавить себя
    if text == "➕ Добавить себя":
        context.user_data.clear()
        context.user_data["step"] = "nick"
        await update.message.reply_text("Введите ваш ник в PUBG:")

    elif context.user_data.get("step") == "nick":
        context.user_data["nickname"] = text
        context.user_data["step"] = "server"
        await update.message.reply_text("Выберите сервер:", reply_markup=ReplyKeyboardMarkup(servers, resize_keyboard=True))

    elif context.user_data.get("step") == "server":
        context.user_data["server"] = text
        context.user_data["step"] = "mode"
        await update.message.reply_text("Выберите режим:", reply_markup=ReplyKeyboardMarkup(modes, resize_keyboard=True))

    elif context.user_data.get("step") == "mode":
        context.user_data["mode"] = text
        context.user_data["step"] = "rank"
        await update.message.reply_text("Выберите ранг:", reply_markup=ReplyKeyboardMarkup(ranks, resize_keyboard=True))

    elif context.user_data.get("step") == "rank":
        context.user_data["rank"] = text
        context.user_data["step"] = "mic"
        await update.message.reply_text("Есть микрофон?", reply_markup=ReplyKeyboardMarkup(mic_options, resize_keyboard=True))

    elif context.user_data.get("step") == "mic":
        context.user_data["mic"] = text
        # Удаляем старую анкету пользователя
        players = [p for p in players if p["user_id"] != user.id]
        # Сохраняем новую
        players.append({
            "user_id": user.id,
            "username": user.username,
            "nickname": context.user_data["nickname"],
            "server": context.user_data["server"],
            "mode": context.user_data["mode"],
            "rank": context.user_data["rank"],
            "mic": context.user_data["mic"]
        })
        context.user_data.clear()
        await update.message.reply_text("Анкета сохранена!", reply_markup=menu)

    # 🔎 Найти тиммейтов
    elif text == "🔎 Найти тиммейтов":
        if not players:
            await update.message.reply_text("Пока нет игроков.", reply_markup=menu)
            return

        # Фильтруем по серверу (пример)
        servers_keyboard = ReplyKeyboardMarkup(servers, resize_keyboard=True)
        context.user_data["step"] = "filter_server"
        await update.message.reply_text("Выберите сервер для поиска:", reply_markup=servers_keyboard)

    elif context.user_data.get("step") == "filter_server":
        context.user_data["filter_server"] = text
        context.user_data["step"] = "filter_mode"
        await update.message.reply_text("Выберите режим для поиска:", reply_markup=ReplyKeyboardMarkup(modes, resize_keyboard=True))

    elif context.user_data.get("step") == "filter_mode":
        context.user_data["filter_mode"] = text
        context.user_data["step"] = "filter_rank"
        await update.message.reply_text("Выберите минимальный ранг для поиска:", reply_markup=ReplyKeyboardMarkup(ranks, resize_keyboard=True))

    elif context.user_data.get("step") == "filter_rank":
        filter_rank = text
        filter_server = context.user_data.get("filter_server")
        filter_mode = context.user_data.get("filter_mode")

        # Фильтруем игроков
        filtered_players = []
        for p in players:
            if p["server"] == filter_server and p["mode"] == filter_mode:
                # Сравниваем ранги по списку
                rank_order = ["Bronze","Silver","Gold","Platinum","Diamond","Crown","Ace","Conqueror"]
                if rank_order.index(p["rank"]) >= rank_order.index(filter_rank):
                    filtered_players.append(p)

        if not filtered_players:
            await update.message.reply_text("Игроков по фильтру не найдено.", reply_markup=menu)
        else:
            msg = "Игроки по фильтру:\n\n"
            for p in filtered_players:
                username = f"@{p['username']}" if p["username"] else "Нет username"
                msg += (f"Ник: {p['nickname']}\nСервер: {p['server']}\n"
                        f"Режим: {p['mode']}\nРанг: {p['rank']}\n"
                        f"Микрофон: {p['mic']}\nСвязь: {username}\n\n")
            await update.message.reply_text(msg, reply_markup=menu)

        context.user_data.clear()

    # ❌ Удалить анкету
    elif text == "❌ Удалить анкету":
        players = [p for p in players if p["user_id"] != user.id]
        await update.message.reply_text("Анкета удалена.", reply_markup=menu)

# Запуск бота
app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT, handle))

print("Бот запущен")
app.run_polling()