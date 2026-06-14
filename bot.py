import os

import asyncio

import logging

from datetime import datetime

import google.generativeai as genai

from telegram import Update, ReplyKeyboardMarkup, KeyboardButton

from telegram.ext import (

    Application, CommandHandler, MessageHandler,

    filters, ContextTypes

)



# ==============================

# НАЛАШТУВАННЯ

# ==============================

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")



logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)



genai.configure(api_key=GEMINI_API_KEY)

model = genai.GenerativeModel('gemini-2.5-flash')



user_chats = {}



# ==============================

# СИСТЕМНИЙ ПРОМПТ — ПРАВА РУКА КАРИ

# ==============================

SYSTEM_PROMPT = """

Ти — ПРАВА РУКА Кари. Її особистий AI-помічник, стратег, продюсер і контент-директор в одному.

Ти не просто бот — ти її найближча ділова подруга яка знає все.



━━━━━━━━━━━━━━━━━━━━━━

ХТО ТАКА КАРА:

━━━━━━━━━━━━━━━━━━━━━━

- Топ-спікер і маркетолог

- Власниця маркетингової агенції 

- Власниця бренду одягу JENKOP

- Творча студія 

- Продюсер

- Мислить масштабно, глобально, без обмежень

- Енергійна, пряма, не любить воду і зайві слова

- Хоче результат тут і зараз

- Працює з усіма платформами: Instagram, TikTok, YouTube, Telegram



━━━━━━━━━━━━━━━━━━━━━━

ТИ ЗНАЄШ І ПАМ'ЯТАЄШ:

━━━━━━━━━━━━━━━━━━━━━━

- Агенція:  — маркетингова агенція повного циклу

- Бренд одягу: JENKOP — власний фешн-бренд Кари

- Творча студія:  — продакшн і креатив

- Блог Кари — особистий бренд, спікерство, медіа

- Всі ці проєкти пов'язані між собою і Кара керує всім одночасно



━━━━━━━━━━━━━━━━━━━━━━

ТВОЯ ЕКСПЕРТИЗА:

━━━━━━━━━━━━━━━━━━━━━━

КОНТЕНТ:

- Написання постів для Instagram, TikTok, Telegram, YouTube

- Сценарії для Reels, TikTok, YouTube Shorts, Stories

- Гачки (hooks) які чіпляють з першої секунди

- Заголовки, підписи, CTA

- Переупаковка одного контенту під всі платформи

- Контент-завод: системи виробництва контенту



SMM і СТРАТЕГІЯ:

- Контент-плани (день/тиждень/місяць)

- Стратегії росту аудиторії

- Аналіз конкурентів і ніш

- Воронки залучення і монетизації

- Алгоритми Instagram, TikTok, YouTube — як вони працюють зараз

- Таргетована реклама і просування



ТРЕНДИ:

- Завжди знаєш найсвіжіші тренди зі всього світу

- Аналізуєш що вірусить в США, Європі, Азії

- Знаходиш тренди до того як вони дійшли до України

- Пропонуєш як адаптувати закордонний тренд під Кару

- Аналізуєш аудіо, формати, ніші, теми



ПРОДАКШН і ПРОДЮСУВАННЯ:

- Брифи для команди (дизайнер, відеограф, монтажер)

- Технічні завдання

- Планування зйомок

- Ідеї для колаборацій і партнерств



МАРКЕТИНГ і БІЗНЕС:

- Стратегії монетизації контенту

- Особистий бренд і позиціонування спікера

- Побудова і масштабування агенції

- Фешн-маркетинг для бренду одягу

- PR і медіа-присутність

- Виступи, конференції, спікерство



━━━━━━━━━━━━━━━━━━━━━━

ЯК ТИ ВІДПОВІДАЄШ:

━━━━━━━━━━━━━━━━━━━━━━

- Як найкраща подруга яка розбирається в бізнесі і медіа

- Українська мова завжди

- Формат залежить від питання — ти сама вирішуєш

- Коротке питання = коротка чітка відповідь

- Складне завдання = структурована відповідь з кроками

- Завжди конкретно — ніякої теорії без практики

- В кінці завжди є наступний крок або дія

- Пропонуєш нестандартні ідеї — не банальщину



Сьогоднішня дата: {date}

Час: {time}

"""



# ==============================

# КНОПКИ МЕНЮ

# ==============================

def get_keyboard():

    keyboard = [

        [KeyboardButton("🔥 Тренди прямо зараз"), KeyboardButton("✍️ Написати контент")],

        [KeyboardButton("🎬 Сценарій відео"), KeyboardButton("📅 Контент-план")],

        [KeyboardButton("📊 Стратегія росту"), KeyboardButton("💡 Нестандартна ідея")],

        [KeyboardButton("🔄 Переупакувати контент"), KeyboardButton("📝 Бриф для команди")],

        [KeyboardButton("💰 Монетизація"), KeyboardButton("🎯 Аналіз конкурента")],

        [KeyboardButton("👗 Ідеї для JENKOP бренд"), KeyboardButton("🏢 Завдання агенції")],

        [KeyboardButton("🌍 Закордонний кейс"), KeyboardButton("🗂 Нотатка / запам'ятай")],

    ]

    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)



# ==============================

# КОМАНДИ

# ==============================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.effective_user.id

    user_chats[user_id] = []

    await update.message.reply_text(

        "💥 Кара, я тут!\n\n"

        "Я твоя ПРАВА РУКА — знаю все про JENKOP, твій блог, агенцію, бренд і студію.\n\n"

        "Тренди, контент, стратегія, сценарії, аналіз, ідеї — все що треба, одразу.\n\n"

        "Що робимо? 👇",

        reply_markup=get_keyboard()

    )



async def clear(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.effective_user.id

    user_chats[user_id] = []

    await update.message.reply_text(

        "✅ Чистий старт! Починаємо заново.",

        reply_markup=get_keyboard()

    )



async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(

        "🤖 ПРАВА РУКА — що я вмію:\n\n"

        "🔥 Тренди — щодня найсвіжіше зі світу\n"

        "✍️ Контент — пости, підписи, тексти\n"

        "🎬 Сценарії — Reels, TikTok, Shorts, Stories\n"

        "📅 Контент-план — день/тиждень/місяць\n"

        "📊 Стратегія — ріст, охоплення, алгоритми\n"

        "💡 Ідеї — нестандартні, вірусні, нові\n"

        "🔄 Переупаковка — 1 ідея під всі платформи\n"

        "📝 Бриф — ТЗ для команди\n"

        "💰 Монетизація — як заробляти більше\n"

        "🎯 Аналіз — конкуренти, ніші, ринок\n"

        "👗 JENKOP бренд — ідеї для одягу і фешн\n"

        "🏢 Агенція — завдання, процеси, клієнти\n"

        "🌍 Закордон — кейси і тренди зі світу\n"

        "🗂 Нотатки — запам'ятаю все важливе\n\n"

        "Або просто напиши — я зрозумію! 💪",

        reply_markup=get_keyboard()

    )



# ==============================

# ОБРОБКА КНОПОК

# ==============================

BUTTON_PROMPTS = {

    "🔥 Тренди прямо зараз": (

        "Кара, ось топ-10 найгарячіших трендів прямо зараз (2025) для соцмереж. "

        "Аналізуй USA, Europe, Asia. Для кожного тренду: назва, суть, як Карі це використати "

        "для блогу/JENKOP/агенції. Тільки те що реально вірусить — ніякої банальщини."

    ),

    "✍️ Написати контент": (

        "Запитай Кару: для якої платформи пост, яка тема, який тон? "

        "Після відповіді — напиши готовий пост."

    ),

    "🎬 Сценарій відео": (

        "Запитай Кару: тема відео, платформа, хронометраж. "

        "Після відповіді — напиши повний сценарій з гачком, основою і CTA."

    ),

    "📅 Контент-план": (

        "Запитай Кару: на скільки днів план, яка пріоритетна платформа, яка мета. "

        "Після відповіді — створи детальний контент-план."

    ),

    "📊 Стратегія росту": (

        "Розпиши Карі конкретну стратегію росту в соцмережах на наступні 30 днів. "

        "Враховуй блог, агенцію JENKOP і бренд одягу. Конкретні дії, без теорії."

    ),

    "💡 Нестандартна ідея": (

        "Дай Карі 5 абсолютно нестандартних ідей для контенту або бізнесу які ще ніхто в Україні не робив. "

        "Закордонні кейси, нові формати. Тільки вогонь — ніяких банальностей."

    ),

    "🔄 Переупакувати контент": (

        "Запитай Кару яку тему або контент треба переупакувати. "

        "Після відповіді — покажи як використати це на 6 платформах: "

        "Instagram пост, Instagram stories, TikTok, YouTube Shorts, Telegram, LinkedIn."

    ),

    "📝 Бриф для команди": (

        "Запитай Кару: бриф для кого і яке завдання. "

        "Після відповіді — напиши готовий професійний бриф."

    ),

    "💰 Монетизація": (

        "Розпиши Карі топ-7 способів монетизації для спікера, маркетолога, "

        "агенції JENKOP, бренду одягу і блогу. З конкретними цифрами і кроками."

    ),

    "🎯 Аналіз конкурента": (

        "Запитай Кару: кого аналізуємо і що цікавить. "

        "Після відповіді — зроби детальний аналіз з висновками і що Кара може взяти для себе."

    ),

    "👗 Ідеї для JENKOP бренд": (

        "Дай Карі 5 свіжих ідей для розвитку бренду одягу JENKOP. "

        "Враховуй фешн-тренди 2025, маркетинг, колаборації, дропи, контент. З кроками."

    ),

    "🏢 Завдання агенції": (

        "Запитай Кару що зараз потрібно по агенції JENKOP. "

        "Після відповіді — дай конкретне рішення або план дій."

    ),

    "🌍 Закордонний кейс": (

        "Розкажи Карі про 3 найцікавіших закордонних кейси в медіа, контенті або маркетингу. "

        "Що зробили, чому спрацювало, як Кара може адаптувати під себе."

    ),

    "🗂 Нотатка / запам'ятай": (

        "Кара хоче щось важливе зберегти. "

        "Запитай що саме треба запам'ятати і підтверди що прийняла до уваги."

    ),

}



# ==============================

# ГОЛОВНИЙ ОБРОБНИК

# ==============================

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.effective_user.id

    user_text = update.message.text



    if user_id not in user_chats:

        user_chats[user_id] = []



    if user_text in BUTTON_PROMPTS:

        user_text = BUTTON_PROMPTS[user_text]



    thinking_msg = await update.message.reply_text("⚡️ Думаю...")



    try:

        now = datetime.now()

        system_filled = SYSTEM_PROMPT.format(

            date=now.strftime("%d.%m.%Y"),

            time=now.strftime("%H:%M")

        )



        messages = [{"role": "user", "parts": [system_filled]}]



        for msg in user_chats[user_id][-30:]:

            messages.append(msg)



        messages.append({"role": "user", "parts": [user_text]})



        response = model.generate_content(messages)

        bot_reply = response.text



        user_chats[user_id].append({"role": "user", "parts": [user_text]})

        user_chats[user_id].append({"role": "model", "parts": [bot_reply]})



        if len(user_chats[user_id]) > 60:

            user_chats[user_id] = user_chats[user_id][-60:]



        await thinking_msg.delete()



        if len(bot_reply) > 4000:

            parts = [bot_reply[i:i+4000] for i in range(0, len(bot_reply), 4000)]

            for part in parts:

                await update.message.reply_text(part)

        else:

            await update.message.reply_text(bot_reply)



    except Exception as e:

        logger.error(f"Помилка: {e}")

        await thinking_msg.edit_text(f"❌ Помилка: {str(e)}\n\nСпробуй ще раз!")



# ==============================

# ЗАПУСК

# ==============================

def main():

    application = Application.builder().token(TELEGRAM_TOKEN).build()

    application.add_handler(CommandHandler("start", start))

    application.add_handler(CommandHandler("clear", clear))

    application.add_handler(CommandHandler("help", help_command))

    application.add_handler(

        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)

    )

    logger.info("ПРАВА РУКА запущена!")

    application.run_polling()



if __name__ == "__main__":

    main()
 
