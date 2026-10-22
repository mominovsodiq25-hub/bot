import asyncio
import os

from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    BotCommand,
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    Message,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
)

# ====== SOZLAMALAR ======
BOT_TOKEN = os.getenv("BOT_TOKEN", "8609401871:AAHhnK9w9DA0wD19EBuFvICN3d7l4GNc8ks")  # @BotFather dan olinadi
ADMIN_PHONE = "+998956168000"          # tugma bosilganda ochiladigan raqam
ADMIN_PHONE_VIEW = "95 616 80 00"      # ekranda ko'rinadigan ko'rinishi
ADMIN_CHAT_ID = None                   # ixtiyoriy: arizalar kelishi uchun admin yoki guruh ID (masalan 123456789)

COURSES = [
    "🇬🇧 Ingliz tili",
    "➗ Matematika",
    "🇩🇪 Nemis tili",
    "🇰🇷 Koreys tili",
    "💻 IT dasturlash",
    "🖥 Kompyuter savodxonligi",
    "⚡ Intensiv",
    "🤖 Sun'iy intellekt",
]


STANDARD_PRICE = "💰 Narxi: <b>300 000 so'm</b>\n📅 1 oyda 26 kun"
PREMIUM_PRICE = (
    "💰 Narxi:\n"
    "• <b>490 000 so'm</b> — 1 oyda 13 kun\n"
    "• <b>1 000 000 so'm</b> — 1 oyda 26 kun"
)
PRICES = [
    STANDARD_PRICE,  # Ingliz tili
    STANDARD_PRICE,  # Matematika
    STANDARD_PRICE,  # Nemis tili
    STANDARD_PRICE,  # Koreys tili
    PREMIUM_PRICE,   # IT dasturlash
    PREMIUM_PRICE,   # Kompyuter savodxonligi
    PREMIUM_PRICE,   # Intensiv
    PREMIUM_PRICE,   # Sun'iy intellekt
]

ABOUT_TEXT = (
    "ℹ️ <b>Peak IT Academy haqida</b>\n\n"
    "📅 2025 yil noyabrda tashkil topgan.\n"
    "📍 Manzil: Jizzax shahri, 6-maktab ro'parasi.\n"
    "📄 Asos: Dasturiy mahsulot va axborot texnologiyalari texnologik parki "
    "direksiyasi mas'uliyati cheklangan jamiyatning 2023 yil 29 sentabrdagi "
    "№14/27-son qarori."
)


class Form(StatesGroup):
    name = State()
    phone = State()


dp = Dispatcher()


def courses_kb() -> InlineKeyboardMarkup:
    rows = []
    for i in range(0, len(COURSES), 2):
        rows.append(
            [
                InlineKeyboardButton(text=c, callback_data=f"course:{i + j}")
                for j, c in enumerate(COURSES[i : i + 2])
            ]
        )
    rows.append([InlineKeyboardButton(text="ℹ️ Biz haqimizda", callback_data="about")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


@dp.message(Command("about"))
async def about_cmd(message: Message):
    await message.answer(ABOUT_TEXT, reply_markup=courses_kb(), parse_mode="HTML")


@dp.callback_query(F.data == "about")
async def about_cb(call: CallbackQuery):
    back = InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="⬅️ Kurslarga qaytish", callback_data="back")]]
    )
    await call.message.answer(ABOUT_TEXT, reply_markup=back, parse_mode="HTML")
    await call.answer()


@dp.callback_query(F.data == "back")
async def back_cb(call: CallbackQuery):
    await call.message.answer("Kerakli kursni tanlang 👇", reply_markup=courses_kb())
    await call.answer()


@dp.message(CommandStart())
async def start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "👋 <b>Peak IT Academy</b>ga xush kelibsiz!\n\n"
        "Bizda quyidagi yo'nalishlar bor. Kerakli kursni tanlang 👇",
        reply_markup=courses_kb(),
        parse_mode="HTML",
    )


@dp.callback_query(F.data.startswith("course:"))
async def choose_course(call: CallbackQuery, state: FSMContext):
    idx = int(call.data.split(":")[1])
    course = COURSES[idx]
    await state.update_data(course=course)
    await state.set_state(Form.name)
    await call.message.answer(
        f"✅ Siz tanladingiz: <b>{course}</b>\n\n"
        f"{PRICES[idx]}\n\n"
        "✍️ F.I.SH ni kiriting:",
        parse_mode="HTML",
    )
    await call.answer()


@dp.message(Form.name, F.text)
async def get_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text.strip())
    await state.set_state(Form.phone)
    kb = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="📱 Raqamimni yuborish", request_contact=True)]],
        resize_keyboard=True,
        one_time_keyboard=True,
    )
    await message.answer("📞 Telefon raqamingizni kiriting:", reply_markup=kb)


@dp.message(Form.phone, F.contact | F.text)
async def get_phone(message: Message, state: FSMContext, bot: Bot):
    phone = message.contact.phone_number if message.contact else message.text.strip()
    data = await state.get_data()
    await state.clear()

    if ADMIN_CHAT_ID:
        await bot.send_message(
            ADMIN_CHAT_ID,
            "🆕 <b>Yangi ariza</b>\n"
            f"📚 Kurs: {data['course']}\n"
            f"👤 F.I.SH: {data['name']}\n"
            f"📞 Telefon: {phone}\n"
            f"🔗 Telegram: @{message.from_user.username or 'yo`q'}",
            parse_mode="HTML",
        )

    kb = InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="📞 Qo'ng'iroq qilish", callback_data="call_admin")]]
    )
    await message.answer("✅ Arizangiz qabul qilindi!", reply_markup=ReplyKeyboardRemove())
    await message.answer(
        f"☎️ Admin raqami: <b>{ADMIN_PHONE_VIEW}</b>\n"
        "Qo'ng'iroq qilish uchun tugmani bosing 👇",
        reply_markup=kb,
        parse_mode="HTML",
    )


@dp.callback_query(F.data == "call_admin")
async def call_admin(call: CallbackQuery, bot: Bot):
    # Telegram inline tugmalarda tel: havolasini qo'llamaydi, shuning uchun
    # kontakt kartasi yuboriladi — undagi "Call" tugmasi telefon ilovasini ochadi.
    await bot.send_contact(
        chat_id=call.message.chat.id,
        phone_number=ADMIN_PHONE,
        first_name="Peak IT Academy",
        last_name="Admin",
    )
    await call.answer()


async def main():
    bot = Bot(BOT_TOKEN)
    await bot.set_my_commands(
        [
            BotCommand(command="start", description="Boshlash"),
            BotCommand(command="about", description="Biz haqimizda"),
        ]
    )
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
