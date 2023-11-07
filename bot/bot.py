import os
import config
import telebot
from telebot import types

bot = telebot.TeleBot(config.BOT_TOKEN)


class Animals:
    def __init__(self):
        self.penguins = False
        self.bears = False


animal_detection = Animals()


def check_empty():
    if animal_detection.bears == False and animal_detection.penguins == False:
        return True
    else:
        return False


@bot.message_handler(commands=['start'])
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
        animal_detection.penguins = True
    elif call.data == "add_bears":
        bot.answer_callback_query(call.id, "Теперь вы следите за медведями!")
        animal_detection.bears = True
    elif call.data == "rem_penguins":
        bot.answer_callback_query(call.id, "Теперь вы не следите за пингвинами!")
        animal_detection.penguins = False
    elif call.data == "rem_bears":
        bot.answer_callback_query(call.id, "Теперь вы не следите за медведями!")
        animal_detection.bears = False
    elif call.data == "current_penguins":
        with open('../img/pinguin.png', 'rb') as photo:
            bot.send_photo(call.message.chat.id, photo)
    elif call.data == "current_bears":
        with open('../img/pinguin.png', 'rb') as photo:
            bot.send_photo(call.message.chat.id, photo)


bot.infinity_polling()