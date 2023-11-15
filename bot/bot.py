# Without this, functions from `src/*` cannot be imported
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

bot = telebot.TeleBot(config.BOT_TOKEN)

daemon_processes = {
    'bird': None,
    'bear': None
}


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
                           f"Ого, неожиданно обнаружен(ы) объект(ы) типа {', '.join(map(repr, unexpected_objects))}!")


class Animals:
    def __init__(self):
        self.birds = None
        self.bears = None

        # Map animal types to corresponding field names
        self.field_mapping = {
            'bird': 'birds',
            'bear': 'bears'
        }

    def get_field_name(self, animal_type):
        field_name = self.field_mapping.get(animal_type, None)
        if not hasattr(self, field_name):
            raise Exception(f"No field with name '{field_name}' found. "
                            f"Mapping for animal_type='{animal_type}' is unsuccessful.")
        return field_name

    def open_stream(self, animal_type):
        # Check that the given animal type is valid
        if animal_type not in video_sources.keys():
            raise Exception(f"Animal of type '{animal_type}' is not considered by our bot.")

        # Based on the given animal type, get the name of the field
        field_name = self.get_field_name(animal_type)

        # Return if the stream is already opened
        if getattr(self, field_name) is not None:
            return

        source_path = video_sources[animal_type]    # Get source path
        stream = start_camgear_stream(source_path)  # Open stream
        setattr(self, field_name, stream)           # Update the corresponding field

    def close_stream(self, animal_type):
        # Check that the given animal type is valid
        if animal_type not in video_sources.keys():
            raise Exception(f"Animal of type '{animal_type}' is not considered by our bot.")

        # Based on the given animal type, get the name of the field
        field_name = self.get_field_name(animal_type)

        if getattr(self, field_name) is not None:
            stop_camgear_stream(getattr(self, field_name))  # Close stream
            setattr(self, field_name, None)                 # Update the corresponding field

    def start_daemon_process(self, animal_type, chat_id):
        # Check that the given animal type is valid
        if animal_type not in daemon_processes.keys():
            raise Exception(f"Unknown animal of type '{animal_type}'. Cannot start a daemon process.")

        # Check that the daemon process has not been started yet
        if daemon_processes[animal_type] is not None:
            return

        # Based on the given animal type, get the name of the field
        field_name = self.get_field_name(animal_type)

        # Create a daemon process and start it
        new_daemon_process = multiprocessing.Process(target=find_unexpected_objects_in_daemon(
            getattr(self, field_name), animal_type, chat_id
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


def check_empty():
    if animal_detection.bears is None and animal_detection.birds is None:
        return True
    else:
        return False


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
    birds_btn = types.InlineKeyboardButton("🐧 Пингвины", callback_data="add_penguins")
    bears_btn = types.InlineKeyboardButton("🐻‍❄️ Медведи", callback_data="add_bears")
    markup.add(birds_btn, bears_btn)
    bot.send_message(message.chat.id, "Выберите за кем хотите следить:", reply_markup=markup)


@bot.message_handler(commands=['remove'])
def choose_animal(message):
    if check_empty():
        bot.send_message(message.chat.id, "Вы еще не выбрали животных")
        return
    markup = types.InlineKeyboardMarkup()
    if animal_detection.birds:
        birds_btn = types.InlineKeyboardButton("🐧 Пингвины", callback_data="rem_penguins")
        markup.add(birds_btn)
    if animal_detection.bears:
        bears_btn = types.InlineKeyboardButton("🐻‍❄️ Медведи", callback_data="rem_bears")
        markup.add(bears_btn)
    bot.send_message(message.chat.id, "Выберите за кем не хотите следить:", reply_markup=markup)


@bot.message_handler(commands=['animals'])
def show_tracked_animals(message):
    tracked_animals = []

    if animal_detection.birds:
        tracked_animals.append("🐧 пингвинами")
    if animal_detection.bears:
        tracked_animals.append("🐻‍❄️ медведями")

    if tracked_animals:
        response = "Вы следите за: " + ", ".join(tracked_animals) + "."
    else:
        response = "Вы пока не следите ни за одним животным."

    bot.send_message(message.chat.id, response)


@bot.message_handler(commands=['now'])
def choose_animal(message):
    if check_empty():
        bot.send_message(message.chat.id, "Вы еще не выбрали животных")
        return
    markup = types.InlineKeyboardMarkup()
    if animal_detection.birds:
        birds_btn = types.InlineKeyboardButton("🐧 Пингвины", callback_data="current_penguins")
        markup.add(birds_btn)
    if animal_detection.bears:
        bears_btn = types.InlineKeyboardButton("🐻‍❄️ Медведи", callback_data="current_bears")
        markup.add(bears_btn)
    bot.send_message(message.chat.id, "Выберите за кем хотите подсмотреть прямо сейчас:", reply_markup=markup)


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    global daemon_processes
    if call.data == "add_penguins":
        bot.answer_callback_query(call.id, "Теперь вы следите за пингвинами!")
        animal_detection.open_stream('bird')
        animal_detection.start_daemon_process('bird', call.message.chat.id)
    elif call.data == "add_bears":
        bot.answer_callback_query(call.id, "Теперь вы следите за медведями!")
        animal_detection.open_stream('bear')
        animal_detection.start_daemon_process('bear', call.message.chat.id)
    elif call.data == "rem_penguins":
        bot.answer_callback_query(call.id, "Теперь вы не следите за пингвинами!")
        animal_detection.close_stream('bird')
        animal_detection.terminate_daemon_process('bird')
    elif call.data == "rem_bears":
        bot.answer_callback_query(call.id, "Теперь вы не следите за медведями!")
        animal_detection.close_stream('bear')
        animal_detection.terminate_daemon_process('bear')
    elif call.data == "current_penguins":
        file_name = get_current_frame(animal_detection.birds)
        with open(file_name, 'rb') as photo:
            bot.send_message(call.message.chat.id, "Вот что происходит у пингвинов прямо сейчас!")
            bot.send_photo(call.message.chat.id, photo)
        os.remove(file_name)
    elif call.data == "current_bears":
        file_name = get_current_frame(animal_detection.bears)
        with open(file_name, 'rb') as photo:
            bot.send_message(call.message.chat.id, "Вот что происходит у мишек прямо сейчас!")
            bot.send_photo(call.message.chat.id, photo)
        os.remove(file_name)


bot.infinity_polling()
