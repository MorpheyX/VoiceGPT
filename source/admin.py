import sqlmethods as sql
import openai
from config import dp, types, admin, bot


@dp.message_handler(commands=['stats'])
async def stats(message: types.Message):
    if message.from_user.id == admin:
        sql.fetchall()
        quantity = sql.fetchall.quantity
        await message.answer(f'Users quantity: {quantity}')


@dp.message_handler(commands=['mailing list'])
async def mailing(message: types.Message):
    if message.from_id == admin:
        sql.fetchall()
        users_ids = sql.fetchall.users_ids
        for index, ids in enumerate(users_ids):
            try:
                user_id = ids[index]
                await bot.send_message(user_id, message.text[5:])
            except Exception as error:
                await bot.send_message(message.chat.id, f'Unkown error - {ids}: {error}')
                continue

