import logging
import aiogram.utils.markdown as md
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ParseMode
from aiogram.utils import executor
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from sqlite import db_start
import random


async def on_startup(_):
    await db_start()


logging.basicConfig(level=logging.INFO)

API_TOKEN = '5936956057:AAGmQIRzK1HnRR2HQfMXiCZlQlu9CVgdXwo'

bot = Bot(token=API_TOKEN)

# For example use simple MemoryStorage for Dispatcher.
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


class Hangman1(StatesGroup):
    display = State()
    send = State()
    wl = State()


class Hangman:
    def __init__(self, words, num, lv):
            self.words = words
            self.num = num
            self.lv = lv


ws = ['hello', 'shalom', 'hola', 'privet', 'konichiva']
h1 = Hangman(ws, random.randint(0, 4), 5)
# await h1.play()


def get_game() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton('/play'))

    return kb


def get_cancel_kb() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton('/cancel'))

    return kb


@dp.message_handler(commands=['cancel'], state='*')
async def cmd_cancel(message: types.Message, state: FSMContext):
    if state is None:
        return
    await state.finish()
    await message.reply("Sure, I'll wait!",
                        reply_markup=get_game())


@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message) -> None:
     await message.answer('Welcome! So as to create profile - type /play',
                          reply_markup=get_game())
     await process_hangman(user_id=message.from_user.id)

s = h1.words[h1.num].strip()
a = []
b = []
@dp.message_handler(commands=['play'])
async def process_hangman(message: types.Message):
    global a
    global s
    global b
    for i in range(len(s)):
        a.append('_')
    await message.reply(f"Let's start!\n lives = {h1.lv}\n {' '.join(a)}\n Used: [{' '.join(b)}]\n Enter a letter:",
                        reply_markup=get_cancel_kb())
    await Hangman1.send.set()

@dp.message_handler( state=Hangman1.display)
async def display_hg(message: types.Message):
    global a
    global b
    global s
    go = a.count('_')
    if go == 0:
        await message.answer('GAME OVER!\nYOU WIN!')
        h1.lv = 5
        a = []
        b = []
        s = h1.words[random.randint(0, 4)].strip()
    elif go != 0 and h1.lv == 0:
        await message.answer('GAME OVER!\nYOU LOSE!')
        await message.reply(f"Let's start!\n lives = {h1.lv}\n {' '.join(a)}\n Used: [{' '.join(b)}]")
        h1.lv = 5
        a = []
        b = []
        s = h1.words[random.randint(0, 4)].strip()
    else:
        await message.reply(f"Let's start!\n lives = {h1.lv}\n {' '.join(a)}\n Used: [{' '.join(b)}]\n Enter a letter:")
        await Hangman1.send.set()

@dp.message_handler( state=Hangman1.send)
async def play_hg(message: types.Message):
    global a
    global b
    global s
    res = s.find(message.text)
    if res != -1:
        if a[res] != '_':
            await message.reply('You have already used that letter')
            h1.lv -= 1
        else:
            for i in range(len(s)):
                if s[i] == message.text:
                    a[i] = message.text
            b.append(message.text)
    await Hangman1.display.set()



if __name__ == '__main__':
    executor.start_polling(dp, on_startup=on_startup)