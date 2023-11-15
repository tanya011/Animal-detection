# Emojis of animals available in the bot. Used in messages from the bot.
emojis = {
    'bird': '🐧',
    'bear': '🐻‍❄️'
}

# Declensions of russian words of corresponding animals available in the bot.
word_declensions = {
    'bird': ['Пингвины', 'пингвинов', 'пингвинами'],
    'bear': ['Медведи', 'мишек', 'мишками']
}


def get_nominative(animal_type):
    """
    Returns a string where the russian word of animal type is in the nominative case (именительный падеж)

    :param animal_type: Animal type which word is Russian should be in a specified form.
    :return A string with a correct form of the Russian word.
    """
    if animal_type not in word_declensions.keys():
        raise Exception(f"Unknown animal type {animal_type}.")

    return f"{emojis[animal_type]} {word_declensions[animal_type][0]}"


def get_genitive(animal_type):
    """
    Returns a string where the russian word of animal type is in the genitive case (родительный падеж)

    :param animal_type: Animal type which word is Russian should be in a specified form.
    :return A string with a correct form of the Russian word.
    """
    if animal_type not in word_declensions.keys():
        raise Exception(f"Unknown animal type {animal_type}.")

    return word_declensions[animal_type][1]


def get_instrumental(animal_type):
    """
    Returns a string where the russian word of animal type is in the instrumental case (творительный падеж)

    :param animal_type: Animal type which word is Russian should be in a specified form.
    :return A string with a correct form of the Russian word.
    """
    if animal_type not in word_declensions.keys():
        raise Exception(f"Unknown animal type {animal_type}.")

    return word_declensions[animal_type][2]


def get_emoji(animal_type):
    """
    Returns an emoji for the specified animal type.
    """
    if animal_type not in word_declensions.keys():
        raise Exception(f"Unknown animal type {animal_type}.")

    return emojis[animal_type]
