import os
import threading
from datetime import datetime

import time

from static.sources import video_sources
from img_processing.process_image import check_something_unexpected, print_unexpected_objects_info
from static.word_declensions import get_genitive


# Maps animal type to a daemon process where each frame of the video stream is checked for something unexpected
# Keys are the same as in the `video_sources` dictionary.
# Initially, each value is equal to `None`.
daemon_processes = {animal_type: None for animal_type in video_sources.keys()}

# Used for updating values of `daemon_processes`
lock = threading.Lock()


def start_daemon_process(animal_type, opened_stream, chat_id, bot):
    """
    Creates and starts a daemon process. Inside the process, frames from a live stream are taken and processed in order to find unexpected objects.

    Args:
        animal_type: Type of animal which corresponding daemon process should be started.
        opened_stream: A stream of type `CamGear` where animals of the specified type can be found.
        chat_id: ID of the Telegram chat where the resulting image should be sent to.
        bot: An instance of the Telegram bot.
    """
    global daemon_processes
    global lock

    # Check that the given animal type is valid
    if animal_type not in daemon_processes.keys():
        raise Exception(f"Unknown animal type '{animal_type}'. Cannot start a daemon process.")

    # If `opened_stream` is None, it means the user does not monitor the animal of the specified type.
    if opened_stream is None:
        return

    with lock:
        # Check that the daemon process has not been started yet
        if daemon_processes[animal_type] is not None:
            return

        # Create a daemon process
        new_daemon_process = threading.Thread(
            target=find_unexpected_objects_in_daemon,
            args=(opened_stream, animal_type, chat_id, bot)
        )
        daemon_processes[animal_type] = new_daemon_process

    # Start the process
    new_daemon_process.start()


def terminate_daemon_process(animal_type):
    """
    Terminates a daemon process.
    :param animal_type: Type of animal which corresponding daemon process should be terminated.
    """
    global daemon_processes

    # Check that the given animal type is valid
    if animal_type not in daemon_processes.keys():
        raise Exception(f"Unknown animal of type '{animal_type}'. Cannot start a daemon process.")

    with lock:
        # Check that the daemon process is started
        if daemon_processes[animal_type] is None:
            return

        # Terminate the process
        daemon_processes[animal_type].terminate()
        daemon_processes[animal_type] = None

    # Print that the daemon process is successfully terminated
    print_log_info(animal_type, "The daemon process is terminated.")


def find_unexpected_objects_in_daemon(video_stream, animal_type, chat_id, bot):
    """
    Processes the frames, which are extracted from the video stream, and checks if there are objects unexpected for the given stream.

    Args:
        video_stream: An instance of `CamGear` -- an opened stream source.
        animal_type: Type of animals which are expected to be seen on the video.
        chat_id: ID of the Telegram chat where the resulting image should be sent to.
        bot: An instance of the Telegram bot.
    """
    if animal_type is None:
        raise Exception("Animal type should not be None.")

    # Print that the daemon process is successfully started
    print_log_info(animal_type, "Daemon process is started.")

    while video_stream is not None:
        time.sleep(10)

        # Process frame
        frame = video_stream.read()
        if frame is None:
            break

        file_name, unexpected_objects = check_something_unexpected(frame, animal_type)
        print_unexpected_objects_info(animal_type, unexpected_objects)

        # Send photo to the bot if something unexpected was found
        if len(unexpected_objects) > 0:
            photo = open(file_name, 'rb')
            bot.send_photo(chat_id, photo,
                           f"Ого, у {get_genitive(animal_type)} "
                           f"неожиданно обнаружен(ы) объект(ы) типа {', '.join(map(repr, unexpected_objects))}!")

            os.remove(file_name)  # Remove temporarily created jpg file


def print_log_info(animal_type, message):
    """
    Prints information about the daemon process.

    Args:
        animal_type: Corresponding animal type of the daemon process.
        message: A string representing the log info.
    """
    print(f"'{animal_type}' [{datetime.now().strftime('%y-%m-%d:%H:%M:%S')}]:")
    print(message)
    print()
