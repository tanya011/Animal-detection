# Without this, src.frames cannot be imported
import sys
sys.path.append('../src')

import os
import config
import multiprocessing

import telebot
from telebot import types

from process_stream import get_current_frame, start_camgear_stream, stop_camgear_stream
from sources import video_sources
from word_declensions import get_nominative, get_genitive, get_instrumental, get_emoji


bot = telebot.TeleBot(config.BOT_TOKEN)


def birds_processing():
    while True:
        print("1\n")


bird_process = None


class Animals:
    def __init__(self):
        # Maps animal type to an opened live stream. Keys are the same as in the `video_sources` dictionary.
        # If no stream is opened, value is `None`
        self.opened_streams = {animal_type: None for animal_type in video_sources.keys()}

    def open_stream(self, animal_type):
        # Check that the given animal type is valid
        if animal_type not in video_sources.keys():
            raise Exception(f"Animal of type '{animal_type}' is not considered by our bot.")

        # Return if the stream is already opened
        if self.opened_streams[animal_type] is not None:
            return

        source_path = video_sources[animal_type]    # Get source path
        stream = start_camgear_stream(source_path)  # Open stream
        self.opened_streams[animal_type] = stream   # Update the corresponding field

    def close_stream(self, animal_type):
        # Check that the given animal type is valid
        if animal_type not in video_sources.keys():
            raise Exception(f"Animal of type '{animal_type}' is not considered by our bot.")

        stream = self.opened_streams[animal_type]
        if stream is not None:                       # Check that the stream is opened
            stop_camgear_stream(stream)              # Close stream
            self.opened_streams[animal_type] = None  # Update the corresponding field


animal_detection = Animals()


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    sticker = open('sticker.webp', 'rb')
    bot.send_sticker(message.chat.id, sticker)
    bot.send_message(message.chat.id,
                     ("<b>🐾Добро пожаловать в Animal Detection Bot! 🐾</b> \n \n"
                      "Мы сообщаем интересуню информацию о животных в зоопарке.\n \n"
                      "🙉 Чтобы начать следить за животным введите /add и выберите животное.\n"
                      "🙈 Чтобы перестать следить за животным - введите /remove и выберите животное.\n"
                      "🔍 Чтобы узнать за кем вы следите - введите /animals.\n"
                      "👀 Чтобы подсмотреть за кем-то прямо сейчас /now.\n"
                      ), parse_mode='html')


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
        bot.send_message(message.chat.id, "Вы еще не выбрали животных")


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
        bot.send_message(message.chat.id, "Вы еще не выбрали животных")


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    global bird_process

    # Extract animal type from the callback data
    animal_type = call.data.split("_")[1]

    if call.data.startswith("add_"):
        bot.answer_callback_query(call.id, f"Теперь вы следите за {get_instrumental(animal_type)}!")
        animal_detection.open_stream(animal_type)
        # bird_process = multiprocessing.Process(target=birds_processing())
        # bird_process.start()
    elif call.data.startswith("rem_"):
        bot.answer_callback_query(call.id, f"Теперь вы не следите за {get_instrumental(animal_type)}!")
        animal_detection.close_stream(animal_type)
        # bird_process.terminate()
    elif call.data.startswith("current_"):
        file_name = get_current_frame(animal_detection.opened_streams[animal_type])
        with open(file_name, 'rb') as photo:
            bot.send_message(call.message.chat.id,
                             f"Вот что происходит у {get_genitive(animal_type)} прямо сейчас!")
            bot.send_photo(call.message.chat.id, photo)
        os.remove(file_name)


bot.infinity_polling()
