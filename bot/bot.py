# Without this, src.frames cannot be imported
import sys

sys.path.append('../src')

import os
import config
import telebot
from telebot import types
from frames import get_current_frame
from frames import start_camgear_stream, stop_camgear_stream
from sources import video_sources

bot = telebot.TeleBot(config.BOT_TOKEN)


class Animals:
    def __init__(self):
        self.penguins = None
        self.bears = None

        # Map animal types to corresponding field names
        self.field_mapping = {
            'bird': 'penguins',
            'bear': 'bears'
        }

    def get_field_name(self, animal_type):
        field_name = self.field_mapping.get(animal_type, None)
        if not hasattr(self, field_name):
            raise Exception(f"No field with name '{field_name} found. "
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


animal_detection = Animals()


def check_empty():
    if animal_detection.bears is None and animal_detection.penguins is None:
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
    penguins_btn = types.InlineKeyboardButton("🐧 Пингвины", callback_data="add_penguins")
    bears_btn = types.InlineKeyboardButton("🐻‍❄️ Медведи", callback_data="add_bears")
    markup.add(penguins_btn, bears_btn)
    bot.send_message(message.chat.id, "Выберите за кем хотите следить:", reply_markup=markup)


@bot.message_handler(commands=['remove'])
def choose_animal(message):
    if check_empty():
        bot.send_message(message.chat.id, "Вы еще не выбрали животных")
        return
    markup = types.InlineKeyboardMarkup()
    if animal_detection.penguins:
        penguins_btn = types.InlineKeyboardButton("🐧 Пингвины", callback_data="rem_penguins")
        markup.add(penguins_btn)
    if animal_detection.bears:
        bears_btn = types.InlineKeyboardButton("🐻‍❄️ Медведи", callback_data="rem_bears")
        markup.add(bears_btn)
    bot.send_message(message.chat.id, "Выберите за кем не хотите следить:", reply_markup=markup)


@bot.message_handler(commands=['animals'])
def show_tracked_animals(message):
    tracked_animals = []

    if animal_detection.penguins:
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
    if animal_detection.penguins:
        penguins_btn = types.InlineKeyboardButton("🐧 Пингвины", callback_data="current_penguins")
        markup.add(penguins_btn)
    if animal_detection.bears:
        bears_btn = types.InlineKeyboardButton("🐻‍❄️ Медведи", callback_data="current_bears")
        markup.add(bears_btn)
    bot.send_message(message.chat.id, "Выберите за кем хотите подсмотреть прямо сейчас:", reply_markup=markup)


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == "add_penguins":
        bot.answer_callback_query(call.id, "Теперь вы следите за пингвинами!")
        animal_detection.open_stream('bird')
    elif call.data == "add_bears":
        bot.answer_callback_query(call.id, "Теперь вы следите за медведями!")
        animal_detection.open_stream('bear')
    elif call.data == "rem_penguins":
        bot.answer_callback_query(call.id, "Теперь вы не следите за пингвинами!")
        animal_detection.close_stream('bird')
    elif call.data == "rem_bears":
        bot.answer_callback_query(call.id, "Теперь вы не следите за медведями!")
        animal_detection.close_stream('bear')
    elif call.data == "current_penguins":
        file_name = get_current_frame(animal_detection.penguins)
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
