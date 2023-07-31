import sqlmethods as sql
from config import *
from gtts import gTTS
from aiogram.types import InputFile
from aiogram.dispatcher.filters import Text
from aiogram.types import ParseMode

message_history = {}
user_models = {}
model = 'gpt-3.5-turbo'


def text_to_speech(prompt, filename):
    tts = gTTS(prompt)
    tts.save(filename)
    voice = InputFile(filename)
    return voice


def transcribe_audio(filepath):
    audio_file = open(filepath, 'rb')
    text = openai.Audio.transcribe("whisper-1", audio_file)
    return text


def model_change(user_id, arg):
    global user_models
    user_models[user_id] = arg


def message_add(user_id, prompt):
    global message_history
    if user_id not in message_history:
        message_history[user_id] = []
    message_history[user_id].append(prompt)


def clear():
    message_history.clear()


@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    user = message.from_user
    user_id = message.from_id
    user_username = user['username']
    user_name = user['first_name']
    premium = user['is_premium']
    user_not_exist = sql.check_user(user_id)
    if user_not_exist:
        notify = f'''New user!
ID: {user_id}
username: {user_username}
name: {message.from_user.first_name}
last name: {message.from_user.last_name}
Is premium?: {premium}
        '''
        sql.put_user(user_id, user_name, user_username)
        await bot.send_message(admin, notify)
    else:
        pass
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    models_button = types.KeyboardButton('Models')
    new_chat_button = types.KeyboardButton('New chat')
    keyboard.add(models_button, new_chat_button)
    welcome_text = f"""
Hello {user_name}, I'm VoiceGPT, i can help to you with anything, just ask me what do you want to do or know.
You can also change model by click on 'Models' button.
Or if you want to create new chat , click on 'New chat' button.
Also you can send me voice  and i answer you with voice message.
"""
    await message.reply(welcome_text, reply_markup=keyboard)


@dp.message_handler(Text("Models"))
async def change_model(message: types.Message):
    models = """
Choose model :
GPT3.5-turbo - fast and effective, chat completion.
Davinci - not so effective , so GPT3.5-turbo, but less censorship, text completion.
DALL-e - create image.
    """
    inline_btn_1 = types.InlineKeyboardButton('DALL-e', callback_data='DALL-e')
    inline_btn_2 = types.InlineKeyboardButton('Davinci', callback_data='text-davinci-003')
    inline_btn_3 = types.InlineKeyboardButton('GPT3.5-turbo', callback_data='gpt-3.5-turbo')
    inline_kb1 = types.InlineKeyboardMarkup().add(inline_btn_1, inline_btn_2, inline_btn_3)
    await message.answer(models, reply_markup=inline_kb1)


@dp.message_handler(Text("New chat"))
async def clear_chat(message: types.Message):
    clear()
    await bot.send_message(message.from_id, 'New chat was created succesfully\nYou can start asking')


@dp.callback_query_handler(text='DALL-e')
async def dall_e(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    data = callback_query.data
    model_change(user_id, callback_query.data)
    await bot.send_message(user_id, f'Model succesfully changed to {data}')


@dp.callback_query_handler(text='text-davinci-003')
async def davinci(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    data = callback_query.data
    model_change(user_id, callback_query.data)
    await bot.send_message(user_id, f'Model succesfully changed to {data}')


@dp.callback_query_handler(text='gpt-3.5-turbo')
async def turbo(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    data = callback_query.data
    model_change(user_id, callback_query.data)
    await bot.send_message(user_id, f'Model succesfully changed to {data}')


@dp.message_handler()
async def gpt(message: types.Message):
    messages = await message.answer('Thinking...')
    user_message = message.text
    prompt = {"role": "user", "content": user_message}
    user_id = message.from_user.id
    message_add(user_id, prompt)
    model = user_models.get(user_id, 'gpt-3.5-turbo')
    if model == 'text-davinci-003':
        completion = openai.Completion.create(
            model=model,
            prompt=user_message,
            max_tokens=2000,
            temperature=0
        )
        response = completion['choices'][0]['text']
        await messages.edit_text(response)
    elif model == 'gpt-3.5-turbo':
        completion = openai.ChatCompletion.create(
            model=model,
            messages=message_history[user_id])
        response = completion.choices[0].message['content']
        system_response = {'role': 'system', 'content': response}
        message_add(user_id, system_response)
        await messages.edit_text(response)
    elif model == 'DALL-e':
        response = openai.Image.create(
            prompt=user_message,
            n=1,
            size="1024x1024"
        )
        image_url = response['data'][0]['url']
        await bot.send_photo(message.from_id, image_url)


@dp.message_handler(content_types=['voice'])
async def voice_gpt(message):
    await message.answer('Thinking...')
    file_id = message.voice.file_id
    file = await bot.get_file(file_id)
    file_path = file.file_path
    await bot.download_file(file_path, 'ponxs.mp3')
    text = transcribe_audio('ponxs.mp3').text
    prompt = {"role": "user", "content": text}
    user_id = message.from_user.id
    user_name = message.from_user.first_name
    filename = user_name + text[:5]
    message_add(user_id, prompt)
    model = user_models.get(user_id, 'gpt-3.5-turbo')
    if model == 'text-davinci-003':
        completion = openai.Completion.create(
            model=model,
            prompt=text,
            max_tokens=2000,
            temperature=0
        )
        response = completion['choices'][0]['text']
        voice = text_to_speech(response, filename)
        await bot.send_voice(user_id, voice)
    elif model == 'gpt-3.5-turbo':
        completion = openai.ChatCompletion.create(
            model=model,
            messages=message_history[user_id])
        response = completion.choices[0].message['content']
        system_response = {'role': 'system', 'content': response}
        message_add(user_id, system_response)
        voice = text_to_speech(response, filename)
        await bot.send_voice(user_id, voice)
    elif model == 'DALL-e':
        response = openai.Image.create(
            prompt=text,
            n=1,
            size="1024x1024"
        )
        image_url = response['data'][0]['url']
        await bot.send_photo(message.from_id, image_url)

