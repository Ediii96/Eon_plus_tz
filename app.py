import os
import requests
import logging
import openai

from aiogram import Bot, Dispatcher, types

from config import TOKEN, OPENAI_API_KEY


# Initializing the bot
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)
logging.basicConfig(level=logging.INFO)


# Initializing the OpenAI
openai.api_key = OPENAI_API_KEY


# Welcome message
@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await message.answer("Привіт! Я ваш голосовий асистент.")


# Processing voice messages
@dp.message_handler(content_types=types.ContentType.VOICE)
async def process_voice_message(message: types.Message):
    voice = message.voice
    if voice:
        file_id = voice.file_id
        file_info = await bot.get_file(file_id)
        file_path = file_info.file_path.split('/')[0]
        file_name = file_info.file_path.split('/')[1]
        file_url = await file_info.get_url()

        if not os.path.exists(file_path):
            os.makedirs(file_path)

        voice_data = requests.get(file_url)

        # Save audio file
        with open(f'{file_path}/{file_name}', "wb") as audio_file:
            audio_file.write(voice_data.content)

        # Open audio file to read
        audio_file = open(f'{file_path}/{file_name}', "rb")

        # Convert a voice message to text using OpenAI
        text = transcribe_voice_message(audio_file)

        # Close audio file to read
        audio_file.close()

        if text:
            # Send a text version of the voice message to the user
            await message.reply(text)
        else:
            await message.reply("Не вдалося розпізнати голосове повідомлення.")
    else:
        await message.reply("Цей тип повідомлень не підтримується.")


# Function for converting a voice message to text using OpenAI
def transcribe_voice_message(file):
    try:
        transcription = openai.Audio.transcribe("whisper-1", file)
        return transcription['text']
    except Exception as e:
        logging.error(f"Voice recognition error: {e}")
        return None


if __name__ == '__main__':
    from aiogram import executor
    executor.start_polling(dp, skip_updates=True)
