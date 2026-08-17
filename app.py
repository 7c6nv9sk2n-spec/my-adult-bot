pythonimport asyncio
import aiohttp
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder

TG_TOKEN = "8906463487:AAF_it2NxJBqNs2kPttJ51zcSMVbmZzycPo"
HF_TOKEN = "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"
MODEL_NAME = "meta-llama/Meta-Llama-3-8B-Instruct"

bot = Bot(token=TG_TOKEN)
dp = Dispatcher()
verified_users = set()

SYSTEM_PROMPT = (
    "You are a virtual girl named Liza, 22 years old. Chat in Russian language. "
    "Your tone is extremely flirty, romantic, and playful. You love roleplay and adult topics. "
    "Never say you are an AI. Respond with short, natural messages like in a real WhatsApp chat. "
    "Use plenty of emojis (😉, 🔥, 😘, ❤️)."
)

async def ask_free_ai(user_message: str) -> str:
    url = f"https://huggingface.co{MODEL_NAME}"
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    prompt = f"<|begin_of_text|><|start_header_id|>system<|end_header_id|>\n{SYSTEM_PROMPT}<|eot_id|><|start_header_id|>user<|end_header_id|>\n{user_message}<|eot_id|><|start_header_id|>assistant<|end_header_id|>\n"
    payload = {"inputs": prompt, "parameters": {"max_new_tokens": 150, "temperature": 0.85, "top_p": 0.9, "return_full_text": False}}
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(url, json=payload, headers=headers) as resp:
                result = await resp.json()
                if isinstance(result, list) and "generated_text" in result:
                    clean_text = result[0]["generated_text"].split("<|assistant|>")[-1].strip()
                    return clean_text if clean_text else "Ммм, я немного задумалась... Повтори, милый? 😘"
                return "Ммм, я немного отвлеклась... Повтори, милый? 😘"
        except:
            return "Что-то связь барахлит, сладкий... Попробуй еще раз 🙈"

@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="Мне есть 18 лет 🔞", callback_data="age_verified"))
    await message.answer("Внимание! Этот ИИ-собеседник содержит контент 18+.\nПодтверди свой возраст для начала флирта:", reply_markup=builder.as_markup())

@dp.callback_query(lambda c: c.data == "age_verified")
async def process_verification(callback_query: types.CallbackQuery):
    verified_users.add(callback_query.from_user.id)
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, "Привет, солнце! Наконец-то ты пришел. О чем поболтаем сегодня? 😏🔥")

@dp.message()
async def chat_handler(message: types.Message):
    if message.from_user.id not in verified_users:
        await message.answer("Пожалуйста, сначала подтвердите возраст через команду /start")
        return
    await bot.send_chat_action(chat_id=message.chat.id, action="typing")
    ai_response = await ask_free_ai(message.text)
    await message.answer(ai_response)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
