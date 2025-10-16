import os
import asyncio
from flask import Flask, request, Response
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

# === Настройки ===
TG_TOKEN = os.environ["TG_BOT_TOKEN"]
KOYEB_HOST = os.environ.get("KOYEB_HOST")  # например your-app.koyeb.app
WEBHOOK_PATH = f"/webhook/{TG_TOKEN}"
WEBHOOK_URL = f"https://{KOYEB_HOST}{WEBHOOK_PATH}" if KOYEB_HOST else None
TARGET_CHAT_ID = int(os.environ.get("TARGET_CHAT_ID", "0"))

# === Инициализация ===
bot = Bot(token=TG_TOKEN)
dp = Dispatcher()
app = Flask(__name__)

# === Состояния ===
class ReportForm(StatesGroup):
    nickname = State()
    date = State()
    activity = State()
    proof = State()

# === Клавиатуры ===
main_menu = ReplyKeyboardMarkup([[KeyboardButton("📨 Отправить отчёт")]], resize_keyboard=True)
activity_kb = ReplyKeyboardMarkup(
    [[KeyboardButton("ФГ")], [KeyboardButton("ЗБ")], [KeyboardButton("Вышка")]],
    resize_keyboard=True, one_time_keyboard=True
)

# === Хэндлеры ===
@dp.message(Command("start"))
async def cmd_start(m: types.Message):
    await m.answer("Привет! Нажми кнопку, чтобы отправить отчёт.", reply_markup=main_menu)

@dp.message(lambda m: m.text == "📨 Отправить отчёт")
async def start_report(m: types.Message, state: FSMContext):
    await m.answer("Введите ваш игровой ник:", reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(ReportForm.nickname)

@dp.message(ReportForm.nickname)
async def set_nick(m: types.Message, state: FSMContext):
    await state.update_data(nickname=m.text)
    await m.answer("Введите дату (например, 16.10.2025):")
    await state.set_state(ReportForm.date)

@dp.message(ReportForm.date)
async def set_date(m: types.Message, state: FSMContext):
    await state.update_data(date=m.text)
    await m.answer("Выберите вид активности:", reply_markup=activity_kb)
    await state.set_state(ReportForm.activity)

@dp.message(ReportForm.activity)
async def set_activity(m: types.Message, state: FSMContext):
    if m.text not in ["ФГ", "ЗБ", "Вышка"]:
        await m.answer("Выбери: ФГ / ЗБ / Вышка")
        return
    await state.update_data(activity=m.text)
    await m.answer("Отправьте доказательство (фото/видео/ссылка):", reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(ReportForm.proof)

@dp.message(ReportForm.proof)
async def finish(m: types.Message, state: FSMContext):
    data = await state.get_data()
    report = (
        f"📋 *Новый отчёт:*\n"
        f"👤 @{m.from_user.username or 'Без_ника'}\n"
        f"🎮 Ник: {data['nickname']}\n"
        f"📅 Дата: {data['date']}\n"
        f"⚔️ Активность: {data['activity']}\n"
    )
    if m.photo:
        await bot.send_photo(TARGET_CHAT_ID or m.chat.id, m.photo[-1].file_id, caption=report, parse_mode="Markdown")
    elif m.video:
        await bot.send_video(TARGET_CHAT_ID or m.chat.id, m.video.file_id, caption=report, parse_mode="Markdown")
    else:
        proof = m.text or "—"
        await bot.send_message(TARGET_CHAT_ID or m.chat.id, report + f"📎 {proof}", parse_mode="Markdown")
    await m.answer("✅ Отчёт отправлен!", reply_markup=main_menu)
    await state.clear()

# === Flask маршруты ===
@app.route("/")
def index():
    return "OK"

@app.route(WEBHOOK_PATH, methods=["POST"])
def webhook():
    update = types.Update(**request.get_json(force=True))
    asyncio.run(dp.feed_update(bot, update))
    return Response(status=200)

# === Устанавливаем webhook ===
async def on_startup():
    if WEBHOOK_URL:
        await bot.delete_webhook()
        await bot.set_webhook(WEBHOOK_URL)
        print("Webhook установлен:", WEBHOOK_URL)

try:
    asyncio.get_event_loop().run_until_complete(on_startup())
except Exception as e:
    print("Ошибка установки webhook:", e)
