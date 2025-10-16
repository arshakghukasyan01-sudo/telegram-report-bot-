
# Telegram Report Bot (Koyeb Deploy)

Простой Telegram-бот для отправки отчётов (ник, дата, активность, доказательство).  
Работает на **Koyeb** через **Flask + aiogram (webhook)**.

---

## 🚀 Шаги для деплоя

1. **Создай репозиторий на GitHub** и добавь файлы:
   - `app.py`
   - `requirements.txt`
   - `Procfile`
   - `README.md`

2. **Создай бота в Telegram:**
   - Напиши `@BotFather`
   - Команда `/newbot`
   - Скопируй токен (`123456:ABC...`)

3. **Зайди в [Koyeb.com](https://www.koyeb.com)**  
   - Нажми **Create Web Service**
   - Подключи свой GitHub-репозиторий
   - В “Run command” введи:  
     `gunicorn -b 0.0.0.0:$PORT app:app`

4. **Добавь переменные окружения (Environment):**
   - `TG_BOT_TOKEN` = твой токен от @BotFather  
   - `KOYEB_HOST` = твой домен (например, `myreportbot.koyeb.app`)  
   - `TARGET_CHAT_ID` = ID канала или группы (можно `0` для личных сообщений)

5. **Нажми Deploy**  
   - После первого запуска посмотри логи — бот сам установит webhook.
   - Открой `https://<твоё-имя>.koyeb.app/` — должно показать `OK`.

6. **Проверь бота в Telegram:**  
   - `/start`  
   - Заполни форму и отправь отчёт 📋

---

💡 Если хочешь узнать `TARGET_CHAT_ID`:
- Добавь бота в канал или группу как администратора.
- Напиши туда сообщение.
- Напиши `@getmyid_bot` — он покажет ID.
