import os
import asyncio
from flask import Flask, request, Response
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

# === Настройки ===
TG_TOKEN = os.environ.get("TG_BOT_TOKEN", "8213431004:AAEZX0ZFe44fD92YScxw-GOvEKQDwY_-fp8")
KOYEB_HOST = os.environ.get("KOYEB_HOST")
WEBHOOK_PATH = f"/webhook/{TG_TOKEN}"
WEBHOOK_URL = f"https://{KOYEB_HOST}{WEBHOOK_PATH}" if KOYEB_HOST else None

TARGET_CHAT_ID = int(os.environ.get("TARGET_CHAT_ID", "-4658562147"))

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
main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📨 Отправить отчёт")]
    ],
    resize_keyboard=True
)

activity_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="ФГ")],
        [KeyboardButton(text="ЗБ")],
        [KeyboardButton(text="Вышка")]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)

# === Команда /start ===
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Привет! 👋\nНажми кнопку, чтобы отправить отчёт:", reply_markup=main_menu)

# === Начало отчёта ===
@dp.message(lambda m: m.text == "📨 Отправить отчёт")
async def start_report(message: types.Message, state: FSMContext):
    await message.answer("Введите ваш игровой ник:", reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(ReportForm.nickname)

# === Ник ===
@dp.message(ReportForm.nickname)
async def set_nickname(message: types.Message, state: FSMContext):
    await state.update_data(nickname=message.text)
    await message.answer("Введите дату (например, 16.10.2025):")
    await state.set_state(ReportForm.date)

# === Дата ===
@dp.message(ReportForm.date)
async def set_date(message: types.Message, state: FSMContext):
    await state.update_data(date=message.text)
    await message.answer("Выберите вид активности:", reply_markup=activity_kb)
    await state.set_state(ReportForm.activity)

# === Активность ===
@dp.message(ReportForm.activity)
async def set_activity(message: types.Message, state: FSMContext):
    if message.text not in ["ФГ", "ЗБ", "Вышка"]:
        await message.answer("Выберите один из вариантов: ФГ / ЗБ / Вышка")
        return
    await state.update_data(activity=message.text)
    await message.answer("Отправьте доказательство (фото, видео или ссылку):", reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(ReportForm.proof)

# === Доказательство ===
@dp.message(ReportForm.proof)
async def finish_report(message: types.Message, state: FSMContext):
    data = await state.get_data()
    report_text = (
        f"📋 *Новый отчёт:*\n"
        f"👤 От: @{message.from_user.username or 'Без_ника'}\n"
        f"🎮 Ник: {data['nickname']}\n"
        f"📅 Дата: {data['date']}\n"
        f"⚔️ Активность: {data['activity']}"
    )

    try:
        if message.photo:
            await bot.send_photo(TARGET_CHAT_ID, message.photo[-1].file_id, caption=report_text, parse_mode="Markdown")
        elif message.video:
            await bot.send_video(TARGET_CHAT_ID, message.video.file_id, caption=report_text, parse_mode="Markdown")
        else:
            await bot.send_message(TARGET_CHAT_ID, f"{report_text}\n📎 {message.text or '—'}", parse_mode="Markdown")
        await message.answer("✅ Отчёт успешно отправлен!", reply_markup=main_menu)
    except Exception as e:
        await message.answer(f"⚠️ Ошибка при отправке отчёта: {e}")

    await state.clear()

# === Flask ===
@app.route("/")
def index():
    return "Bot is running!"

@app.route(WEBHOOK_PATH, methods=["POST"])
def webhook():
    update = types.Update(**request.get_json(force=True))
    asyncio.run(dp.feed_update(bot, update))
    return Response(status=200)

# === Webhook ===
async def on_startup():
    if WEBHOOK_URL:
        await bot.delete_webhook()
        await bot.set_webhook(WEBHOOK_URL)
        print("✅ Webhook установлен:", WEBHOOK_URL)

try:
    asyncio.get_event_loop().run_until_complete(on_startup())
except Exception as e:
    print("Ошибка при установке webhook:", e)