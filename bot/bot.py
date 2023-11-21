# Without this, src.frames cannot be imported
import sys

sys.path.append('../src')
# sys.path.insert(1, '')

# from src.process_stream import get_current_frame

import os
import config
import multiprocessing

import telebot
from telebot import types

from src.process_stream import get_current_frame, get_frames
from src.word_declensions import get_nominative, get_genitive, get_instrumental, get_emoji
from animals import Animals


animal_detection = Animals()


bot = telebot.TeleBot(config.BOT_TOKEN)

available_commands = ['/add', '/remove', '/animals', '/now', '/help']


def generate_cmds_descr():
    return ("🙉 Чтобы начать следить за животным введите /add и выберите животное.\n" +
          "🙈 Чтобы перестать следить за животным - введите /remove и выберите животное.\n" +
          "🔍 Чтобы узнать за кем вы следите - введите /animals.\n" +
          "👀 Чтобы подсмотреть за кем-то прямо сейчас /now.\n" +
          "📖 Чтобы увидеть список комманд, введите /help.\n")


def birds_processing():
    get_frames(animal_detection.opened_streams['bird'], 'bird')


bird_process = None


@bot.message_handler(commands=['start'])
def send_welcome(message):
    sticker = open('sticker.webp', 'rb')
    bot.send_sticker(message.chat.id, sticker)
    bot.send_message(message.chat.id,
                     ("<b>🐾Добро пожаловать в Animal Detection Bot! 🐾</b> \n \n"
                      "Мы сообщаем интересную информацию о животных в зоопарке.\n \n"
                      f'{generate_cmds_descr()}'
                      ), parse_mode='html')


@bot.message_handler(commands=['help'])
def send_welcome(message):
    bot.send_message(message.chat.id, generate_cmds_descr())


@bot.message_handler(commands=['add'])
def choose_animal(message):
    markup = types.InlineKeyboardMarkup()

    # Create buttons for animal types which streams are not opened yet
    for animal_type, opened_stream in animal_detection.opened_streams.items():
        if opened_stream is None:
            btn = types.InlineKeyboardButton(get_nominative(animal_type), callback_data=f"add_{animal_type}")
            markup.add(btn)

    # Send message to the bot
    bot.send_message(message.chat.id, "Выберите за кем хотите следить:", reply_markup=markup)


@bot.message_handler(commands=['remove'])
def choose_animal(message):
    markup = types.InlineKeyboardMarkup()

    # Create buttons for animal types which streams are opened
    for animal_type, opened_stream in animal_detection.opened_streams.items():
        if opened_stream is not None:
            btn = types.InlineKeyboardButton(get_nominative(animal_type), callback_data=f"rem_{animal_type}")
            markup.add(btn)

    # Send message to the bot
    if markup.keyboard:
        bot.send_message(message.chat.id, "Выберите за кем не хотите следить:", reply_markup=markup)
    else:
        bot.send_message(message.chat.id, "Вы еще не выбрали животных.")


@bot.message_handler(commands=['animals'])
def show_tracked_animals(message):
    tracked_animals = []

    # Add names of animal types which streams are opened
    for animal_type, opened_stream in animal_detection.opened_streams.items():
        if opened_stream:
            tracked_animals.append(f"{get_emoji(animal_type)} {get_instrumental(animal_type)}")

    # Generate message
    if tracked_animals:
        response = "Вы следите за:\n    " + "\n    ".join(tracked_animals)
    else:
        response = "Вы пока не следите ни за одним животным."

    # Send message to the bot
    bot.send_message(message.chat.id, response)


@bot.message_handler(commands=['now'])
def choose_animal(message):
    markup = types.InlineKeyboardMarkup()

    # Create buttons for animal types which streams are opened
    for animal_type, opened_stream in animal_detection.opened_streams.items():
        if opened_stream is not None:
            btn = types.InlineKeyboardButton(get_nominative(animal_type), callback_data=f"current_{animal_type}")
            markup.add(btn)

    # Send message to the bot
    if markup.keyboard:
        bot.send_message(message.chat.id, "Выберите за кем хотите подсмотреть прямо сейчас:", reply_markup=markup)
    else:
        bot.send_message(message.chat.id, "Вы еще не выбрали животных.")


@bot.message_handler(func=lambda message: True)
def handle_unknown_command(message):
    if message.text not in available_commands:
        bot.send_message(message.chat.id,
                         (
                             f"Неизвестная комманда '{message.text}'\n\n"
                             "Возможные комманды:\n\n"
                             f"{generate_cmds_descr()}"
                         ), parse_mode='html')


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    global bird_process

    # Delete message with choice
    bot.delete_message(call.message.chat.id, call.message.message_id)

    # Extract animal type from the callback data
    animal_type = call.data.split("_")[1]

    if call.data.startswith("add_"):
        # Send a temporary message to the bot
        tmp_msg = bot.send_message(call.message.chat.id, "Обрабатываем запрос...")
        animal_detection.open_stream(animal_type)
        bot.delete_message(call.message.chat.id, tmp_msg.id)  # Delete the temporary message
        bot.send_message(call.message.chat.id, f"Теперь вы следите за {get_instrumental(animal_type)}!")

        bird_process = multiprocessing.Process(target=birds_processing())
        bird_process.start()

    elif call.data.startswith("rem_"):
        animal_detection.close_stream(animal_type)
        bot.send_message(call.message.chat.id, f"Теперь вы не следите за {get_instrumental(animal_type)}!")
        # bird_process.terminate()

    elif call.data.startswith("current_"):
        # Send a temporary message to the bot
        tmp_msg = bot.send_message(call.message.chat.id, "Обрабатываем запрос...")
        file_name = get_current_frame(animal_detection.opened_streams[animal_type])
        with open(file_name, 'rb') as photo:
            bot.delete_message(call.message.chat.id, tmp_msg.id)  # Delete the temporary message
            bot.send_message(call.message.chat.id,
                             f"Вот что происходит у {get_genitive(animal_type)} прямо сейчас!")
            bot.send_photo(call.message.chat.id, photo)
        os.remove(file_name)


bot.infinity_polling()
