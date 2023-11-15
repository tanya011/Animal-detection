# Without this, functions from `src` cannot be imported
import sys
sys.path.append('../src')

import os
import time
import config
import multiprocessing

import telebot
from telebot import types

from process_stream import get_current_frame, start_camgear_stream, stop_camgear_stream
from process_image import check_something_unexpected
from sources import video_sources
from word_declensions import get_nominative, get_genitive, get_instrumental, get_emoji


# Maps animal type to a daemon process where each frame of the video stream is checked for something unexpected
# Keys are the same as in the `video_sources` dictionary.
# Initially, each value is equal to `None`.
daemon_processes = {animal_type: None for animal_type in video_sources.keys()}


bot = telebot.TeleBot(config.BOT_TOKEN)


def find_unexpected_objects_in_daemon(video_stream, animal_type, chat_id):
    """
    Processes the frames, which are extracted from the video stream, and checks if there are objects unexpected for the given stream.

    Args:
        video_stream: An instance of `CamGear` -- an opened stream source.
        animal_type: Type of animals which are expected to be seen on the video.
        chat_id: chat ID where the resulting image should be sent to. The ID is received from the bot.
    """
    if animal_type is None:
        raise Exception("Animal type should not be None.")

    while video_stream is not None:
        time.sleep(5)

        # Process frame
        frame = video_stream.read()
        if frame is None:
            break
        file_name, unexpected_objects = check_something_unexpected(frame, animal_type)

        # Send photo to the bot if something unexpected was found
        if len(unexpected_objects) > 0:
            photo = open(file_name, 'rb')
            bot.send_photo(chat_id, photo,
                           f"Ого, у {get_genitive(animal_type)} "
                           f"неожиданно обнаружен(ы) объект(ы) типа {', '.join(map(repr, unexpected_objects))}!")


class Animals:
    def __init__(self):
        # Maps animal type to an opened live stream. Keys are the same as in the `video_sources` dictionary.
        # If no stream is opened, value is `None`.
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

    def start_daemon_process(self, animal_type, chat_id):
        # Check that the given animal type is valid
        if animal_type not in daemon_processes.keys():
            raise Exception(f"Unknown animal type '{animal_type}'. Cannot start a daemon process.")

        # Check that the daemon process has not been started yet
        if daemon_processes[animal_type] is not None:
            return

        # Create a daemon process and start it
        new_daemon_process = multiprocessing.Process(target=find_unexpected_objects_in_daemon(
            self.opened_streams[animal_type], animal_type, chat_id
        ))
        daemon_processes[animal_type] = new_daemon_process
        new_daemon_process.start()

    def terminate_daemon_process(self, animal_type):
        # Check that the given animal type is valid
        if animal_type not in daemon_processes.keys():
            raise Exception(f"Unknown animal of type '{animal_type}'. Cannot start a daemon process.")

        if daemon_processes[animal_type] is not None:
            daemon_processes[animal_type].terminate()
            daemon_processes[animal_type] = None


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
    global daemon_processes

    # Extract animal type from the callback data
    animal_type = call.data.split("_")[1]

    if call.data.startswith("add_"):
        bot.answer_callback_query(call.id, f"Теперь вы следите за {get_instrumental(animal_type)}!")
        animal_detection.open_stream(animal_type)
        animal_detection.start_daemon_process(animal_type, call.message.chat.id)
    elif call.data.startswith("rem_"):
        bot.answer_callback_query(call.id, f"Теперь вы не следите за {get_instrumental(animal_type)}!")
        animal_detection.close_stream(animal_type)
        animal_detection.terminate_daemon_process(animal_type)
    elif call.data.startswith("current_"):
        file_name = get_current_frame(animal_detection.opened_streams[animal_type])
        with open(file_name, 'rb') as photo:
            bot.send_message(call.message.chat.id,
                             f"Вот что происходит у {get_genitive(animal_type)} прямо сейчас!")
            bot.send_photo(call.message.chat.id, photo)
        os.remove(file_name)


bot.infinity_polling()
